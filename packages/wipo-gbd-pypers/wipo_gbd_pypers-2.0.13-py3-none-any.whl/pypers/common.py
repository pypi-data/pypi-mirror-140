import argparse
import pypers.utils.utils as ut
from pypers.core.pipelines import Pipeline
from pypers.core.step import Step
import sys
import subprocess
import logging
import glob
import os
import shutil
import tarfile
from distutils.dir_util import copy_tree
from urllib import parse as urlparse
import requests
import paramiko
import getpass
import multiprocessing
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


LOG_DIR = '/data/%(type)s/updates/log'


def build_command_parser(options, doc):
    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    for config in options:
        name = config.pop('name')
        parser.add_argument(*name, **config)
    return parser.parse_args()


def apply_custom(config, custom):
    """
    Replace/add custom values to that in config.
    Config is a dictionary and is expected to have a 'config' section.
    Custom is a list of custom parameters of the form 'a.b.c=value'
    """
    ut.pretty_print("Setting custom params: %s" % custom)
    for c in custom:
        path, v = c.split('=')
        keys = path.split('.')
        if 'config' not in config:
            config['config'] = {}
        param = config['config']
        for key in keys[:-1]:
            if key not in param:
                ut.pretty_print(
                    '*** WARNING: creating new parameter %s (a typo?)' % key)
                param[key] = {}
            param = param[key]
        name = keys[-1]
        if name in param:
            # if already set, preserve type
            ptype = type(param[name])
        else:
            ptype = type(v)
        param.update({name: ptype(v)})


pi = None


def set_pipeline(pipeline):
    global pi
    pi = pipeline


def stop_pipeline(signum, frame):
    global pi
    ut.pretty_print("Signal received: terminating pipeline")
    pi.stop()
    sys.exit()


def exec_cmd(cmd):
    subprocess.call(cmd.split(' '),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)


def init_logger():
    logFormatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5.5s]  %(message)s', '%Y-%m-%d %H:%M:%S')
    rootLogger = logging.getLogger()

    # log to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)
    return rootLogger


def notify_err(conf, coll, files=[], email_all='_all_',
               sender='webadmin@bsidx1n.wipo.int'):
    email_this = conf.get(coll, {}).get('notify', {}).get('error', [])
    if email_this == []:
        email_all = conf[email_all].get('notify', {}).get('error', [])

    subject = '%s: Error executing fetch' % coll.upper()
    body = 'check attachement for details'

    ut.send_mail(sender,
                 email_this + email_all,
                 subject, text=body, files=files)


def notify_success(conf, run_id, releasetar_dir):
    email_all = conf['_all_'].get('notify', {}).get('success', [])

    colls_tm = glob.glob(os.path.join(releasetar_dir % {'type': 'brands'},
                                      '%s_*.tar' % run_id))
    colls_id = glob.glob(os.path.join(releasetar_dir % {'type': 'designs'},
                                      '%s_*.tar' % run_id))

    colls_tm = [os.path.basename(r).replace(
        '%s_' % run_id, '').replace('.tar', '').upper() for r in colls_tm]
    colls_id = [os.path.basename(r).replace(
        '%s_' % run_id, '').replace('.tar', '').upper() for r in colls_id]

    subject = '%s updates released' % run_id

    body = '[%s] TradeMarks: %s\n' % (len(colls_tm), ' - '.join(colls_tm))
    body += '[%s] Designs:    %s\n' % (len(colls_id), ' - '.join(colls_id))

    ut.send_mail('webadmin@bsidx1n.wipo.int', email_all, subject, text=body)


def checkpoint(r, process, conf, logger, fetch_id):
    # all return codes are 0 => success
    if not sum(r):
        return
    ut.notify_err(conf, logger, process, 'FAIL', fetch_id)
    sys.exit(1)


def _mkdirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def do_transfer_prepare(to_release_dir, fetch_id, logger, conf):
    """ create md5 file for tarballs to be transferred to prod env"""
    logger.info('[CHECKSUM:local] START making md5 file')

    tar_files = glob.glob(os.path.join(to_release_dir,  '%s_*.tar' % fetch_id))
    if not len(tar_files):
        return (None, [])

    md5_file = os.path.join(to_release_dir, '%s.md5' % fetch_id)

    logger.info('Creating md5 file for \n\t%s' % '\n\t'.join(tar_files))
    # run checksum on all tar files and store
    # output in md5 file
    cmd = ['/usr/bin/md5sum'] + tar_files
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True)
    stdout, stderr = proc.communicate()
    rc = proc.returncode

    if rc != 0:
        logger.critical('[CHECKSUM:local] FAIL '
                        'could not create md5 file: %s' % stderr)
        ut.notify_err(conf, logger, 'md5 creation', 'FAIL', fetch_id)
        sys.exit(rc)
    with open(md5_file, 'w') as fh:
        fh.write(stdout.decode('utf-8'))

    logger.info('[CHECKSUM:local] DONE  making md5 file')

    return (md5_file, tar_files)


def do_transfer_check(md5, logger):
    fab_file = ut.get_fabfile()

    cmd = ['fab',
           '-f', fab_file,
           'check_md5:%s' % md5]

    logger.info('[CHECKSUM] START checking md5 file on 3 hosts')

    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True)
    stdout, stderr = proc.communicate()
    rc = proc.returncode

    if rc != 0:
        logger.critical('[CHECKSUM] FAIL  checking md5 file %s' % (stderr))
    else:
        logger.info('[CHECKSUM] DONE  checking md5 file on 3 hosts')
    return rc


def do_remote_untar(to_release_dir, dest_dir, fetch_id, logger):
    fab_file = ut.get_fabfile()

    tar_files = glob.glob(os.path.join(to_release_dir, '%s_*.tar' % fetch_id))

    for tar_file in tar_files:
        logger.info('[UNTAR] START untar of %s on 3 hosts' % (tar_file))

        cmd = ['fab',
               '-f', fab_file,
               'untar_release:%s,%s' % (tar_file, dest_dir)]

        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = proc.communicate()
        rc = proc.returncode

        if rc != 0:
            logger.critical('[UNTAR] FAIL  untar of %s ' % (tar_file))
            logger.critical('\n\n%s' % stdout)
            logger.critical('\n\n%s' % stderr)
            return rc

        logger.info('[UNTAR] DONE  untar of %s ' % (tar_file))
    return 0


def do_release_package(colls_to_release, to_release_dir, fetch_id, logger):
    """for every collection:
    - create a tarball of the update in to_release dir"""
    for type, coll, coll_data, coll_release_dir in colls_to_release:

        _mkdirs([coll_release_dir])
        to_release_sdir = os.path.join(to_release_dir % {'type': type},
                                       '%s_%s' % (fetch_id, coll))
        to_release_tar = os.path.join(to_release_dir % {'type': type},
                                      '%s_%s.tar' % (fetch_id, coll))

        logger.info('[COLL:%s] START release data preparation in %s' % (
            coll, to_release_sdir))
        # always ignore icon files (they go to solr)
        ignore_files = ['*-ic.jpg', '*lire7.xml', '*lire.xml']
        if type == 'brands':
            ignore_files.append('*high.png')  # ignore high for brands

        shutil.copytree(coll_data,
                        to_release_sdir,
                        ignore=shutil.ignore_patterns(*ignore_files))

        logger.info('[COLL:%s] DONE  release data preparation in %s' % (
            coll, to_release_sdir))

        logger.info('[COLL:%s] START tarring %s' % (coll, to_release_tar))
        with tarfile.open(to_release_tar, 'w') as tar:
            tar.add(to_release_sdir,
                    arcname=coll_release_dir.replace('/data/%s/' % type, ''))
        shutil.rmtree(to_release_sdir)
        logger.info('[COLL:%s] DONE  tarring %s' % (coll, to_release_tar))


def do_release_staging(colls_to_release, logger):
    """for every collection:
     - release locally to releasedir"""
    for type, coll, coll_data, coll_release_dir in colls_to_release:

        logger.info('[COLL:%s] START release data to %s' % (
            coll, coll_release_dir))
        # using this as shutil.copytree cannot copy into an existing dir
        copy_tree(coll_data, coll_release_dir)
        shutil.rmtree(coll_data)
        logger.info('[COLL:%s] DONE  release data to %s' % (
            coll, coll_release_dir))


def do_optimize(core, logger):
    logger.info('[CORE:%s] START optimizing' % core)

    core_opt_url = 'http://localhost:8080/solr/%s/update' % core
    core_opt_param = {'commit': 'true',
                      'optimize': 'true',
                      'maxSegments': '2'}

    req = requests.get(
        '%s?%s' % (core_opt_url, urlparse.urlencode(core_opt_param)),
        proxies={'http': None})
    logger.info('[CORE:%s] DONE optimizing. SnapShot Now!' % core)


def do_index(type, coll, data, logger):
    logger.info('[INDEX] [%s] START' % coll)

    cmd = ['java', '-jar',
           os.path.join(ut.get_indexer7_root(),
                        'releases/xml-solr7-indexer.jar'),
           '-conf', os.path.join(ut.get_indexer7_root(), 'coll7.yml'),
           '-aspect', 'INDEXER', '-coll', coll, '-docs', data,
           '-lire', 'READ_GEN_SAVE' if type == 'brands' else 'NOPE']

    print(' '.join(cmd))
    rc = subprocess.call(cmd, stdout=None, stderr=subprocess.STDOUT)
    if rc != 0:
        logger.critical('[INDEX] [%s] FAIL -- %s' % (coll, rc))
    logger.info('[INDEX] [%s] END  ' % coll)
    return 0


def do_transfer(host, md5s, f2t):
    print('[TRNSFR:%s] START transfer' % host)
    rc = 1
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(host, username=getpass.getuser())

        sftp = ssh.open_sftp()

        # transfer tars
        for file in f2t:
            sftp.put(file, file)
        # transfer md5
        for md5 in md5s:
            sftp.put(md5, md5)

        sftp.close()
        ssh.close()

        print('[TRNSFR:%s] DONE  transfer' % host)
        rc = 0
    except Exception as e:
        print('[TRNSFR:%s] FAIL  transfer' % host)
    return rc


def mp_transfer_handler(data):
    p = multiprocessing.Pool(3)
    r = p.starmap(do_transfer, data)
    return r


def trim(bw, ori):
    # crop top
    if not np.sum(bw[0]):
        return trim(bw[1:], ori[1:])
    # crop bottom
    elif not np.sum(bw[-1]):
        return trim(bw[:-2], ori[:-2])
    # crop left
    elif not np.sum(bw[:, 0]):
        return trim(bw[:, 1:], ori[:, 1:])
    # crop right
    elif not np.sum(bw[:, -1]):
        return trim(bw[:, :-2], ori[:, :-2])
    return (bw, ori)


def contour_props(contour):
    x1, y1, w, h = cv2.boundingRect(contour)
    x2, y2 = (x1 + w, y1 + h)

    features = cv2.moments(contour)
    area = features['m00']
    # centroid
    cx = int(features['m10'] / area)
    cy = int(features['m01'] / area)
    radius = math.sqrt(area/math.pi)

    return (x1, y1), (x2, y2), (w, h), (cx, cy), radius, area


def draw_diagram(pipelines, spanning_tree=True, path=None):
    # Path allocation
    if not path:
        path = os.path.join(os.environ['PYPERS_HOME'], 'pypers',
                            'pipelines_dag')
        if not os.path.exists(path):
            os.makedirs(path)
    # Cache the properties of already seen steps in order to avoid
    # loading again the same step
    seen_steps = {}
    for pipeline in pipelines:
        dag = Pipeline.create_dag(pipeline)
        # Create the topological order
        topo = list(nx.topological_sort(dag))
        # Suffix for no spanning tree versions
        suffix = '_full' if not spanning_tree else ''
        labels = {}
        # Create the [label] for nodes with iterables
        for node in dag.nodes(data=True):
            class_name = node[1]['class_name']
            # Load only once the node and decide if it has iterables or not
            if not seen_steps.get(class_name, None):
                step = Step.create(class_name)
                has_iterables = step.get_iterables() != []
                seen_steps[class_name] = has_iterables
            # Load from cache the iterables status and append the []
            if seen_steps[class_name]:
                labels[node[0]] = '[%s]' % node[0]
            else:
                labels[node[0]] = node[0]
        if spanning_tree:
            # Spanning tree algorithm: Remove the edges between a node and a
            # successor if there are more than one path.
            edges_to_remove = []
            for node in topo:
                for successor in dag.successors(node):
                    if len(list(nx.all_simple_paths(
                            dag, source=node, target=successor))) > 1:
                        edges_to_remove.append((node, successor))
            for (e, v) in edges_to_remove:
                dag.remove_edge(e, v)
        print("Creating the png for %s in %s" % (pipeline['name'], path))
        # Draw the png
        plt.figure(figsize=(6, 11))
        plt.title('Pipeline: %s' % pipeline['name'])
        pos = graphviz_layout(dag, prog='dot')
        nx.draw(dag, pos, with_labels=True, arrows=True, font_size=12,
                node_size=2000, font_weight='bold', node_color='#B1E4F3',
                labels=labels, edge_color='#999999')
        plt.savefig(os.path.join(path, '%s%s.png' % (pipeline['name'], suffix)))
