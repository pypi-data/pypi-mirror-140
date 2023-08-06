from functools import wraps
import inspect
from fabric.group import ThreadingGroup
from fabric import Connection
from patchwork.transfers import rsync
from invoke import Result, Runner
from .common import build_command_parser
import os
import argparse
from invoke.util import encode_output
import threading


try:
    from importlib.machinery import SourceFileLoader
except ImportError:  # PyPy3
    from importlib._bootstrap import _SourceFileLoader as SourceFileLoader


function_mapping = {}
loader = {}
run_hide = None
settings_holder = {}
host_only_value = None


class Env:
    def __init__(self):
        self.internal_dict = {}

    def __setattr__(self, key, value):
        if key != 'internal_dict':
            self.internal_dict[key] = value
        else:
            super(Env, self).__setattr__(key, value)

    def __getattr__(self, item):
        return self.internal_dict[item]


env = Env()


# Decorators
def task(func):
    if not function_mapping.get(func.__name__, None):
        function_mapping[func.__name__] = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper


def parallel(*args, **kwargs):
    def inner(func):
        if not function_mapping.get(func.__name__, None):
            function_mapping[func.__name__] = {}
        function_mapping[func.__name__]['parallel'] = kwargs

        @wraps(func)
        def wrapper(*args_func, **kargs_func):
            return func(*args_func, **kargs_func)
        return wrapper
    return inner


def hosts(*args, **kwargs):
    def inner(func):
        if not function_mapping.get(func.__name__, None):
            function_mapping[func.__name__] = {}
        a_types = [list, tuple]
        if type(args) in a_types and type(args[0]) in a_types:
            hosts = args[0]
        else:
            hosts = args
        function_mapping[func.__name__]['hosts'] = hosts

        @wraps(func)
        def wrapper(*args_func, **kargs_func):
            return func(*args_func, **kargs_func)
        return wrapper
    return inner


def runs_once(func):
    if not function_mapping.get(func.__name__, None):
        function_mapping[func.__name__] = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        if function_mapping[func.__name__].get('runned', None):
            return
        function_mapping[func.__name__]['runned'] = True
        return func(*args, **kwargs)
    return wrapper


# Context managers
class hide:
    def __init__(self, what):
        global run_hide
        if what == 'output':
            run_hide = 'both'
        if what == 'stdout':
            run_hide = 'out'
        if what == 'stderr':
            run_hide = 'err'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        global run_hide
        run_hide = None


class settings:
    def __init__(self, **kwargs):
        global settings_holder
        settings_holder.update(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        global settings_holder
        settings_holder = {}


class host_only_manager:
    def __init__(self, value):
        global host_only_value, env
        host_only_value = value
        env.host = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        global host_only_value
        host_only_value = None
        env.host = None


# Ported calls
def execute(function_name, *args, **kwargs):
    if not loader.get(function_name):
        raise Exception("Function not found")
    if 'hosts' in kwargs.keys():
        to_return = {}
        for host in kwargs.pop('hosts'):
            with host_only_manager(host):
                to_return[host] = loader[function_name](*args, **kwargs)
        return to_return
    else:
        return loader[function_name](*args, **kwargs)


def run(*args, **kwargs):
    caller_name = inspect.stack()[1].function

    connection = get_connection(function_mapping[caller_name],
                                host_only=host_only_value)
    kwargs['hide'] = run_hide
    if settings_holder.get('warn_only', None) is True:
        try:
            results = connection.run(*args, **kwargs)
        except Exception as e:
            print(e)
            return None
    else:
        results = connection.run(*args, **kwargs)
    to_return = {}
    if isinstance(results, dict):
        for key, result in results.items():
            to_return[key.host] = PypersResults.fromInvoke(result)
    else:
        to_return = PypersResults.fromInvoke(results)
    return to_return


class PypersResults(Result):

    @staticmethod
    def fromInvoke(obj):
        obj.__class__ = PypersResults
        return obj

    def __str__(self):
        return str(self.stdout)


def write_our_output(self, stream, string):
    host = self.context.host
    new_string = []
    for line in string.split('\n'):
        new_string.append('[%s] %s' % (host, line))
    new_string.append("")
    stream.write(encode_output('\n'.join(new_string), self.encoding))
    stream.flush()


# Override function in Runners
Runner.write_our_output = write_our_output


class RsynConnection(Connection):

    def local(self, *args, **kwargs):
        kwargs['hide'] = run_hide
        return super(RsynConnection, self).local(*args, **kwargs)


def rsync_project(*args, **kwargs):
    caller_name = inspect.stack()[1].function
    started_threads = []
    for host in function_mapping[caller_name].get('hosts', []):
        x = threading.Thread(target=rsync_connection, args=(
            host, *args), kwargs=kwargs)
        started_threads.append(x)
    for thread in started_threads:
        thread.start()
    for thread in started_threads:
        thread.join()


def rsync_connection(host, *args, **kwargs):
    connection = RsynConnection(host)
    if settings_holder.get('warn_only', None) is True:
        try:
            rsync(connection, *args, **kwargs)
        except Exception as e:
            print(e)
    else:
        rsync(connection, *args, **kwargs)


def put(*args, **kwargs):
    caller_name = inspect.stack()[1].function
    connection = get_connection(function_mapping[caller_name])
    return connection.put(*args, **kwargs)


def local(*args, **kwargs):
    kwargs['hide'] = run_hide
    return PypersResults.fromInvoke(
        Connection('localhost').local(*args, **kwargs))


# Internals
def get_connection(decorators_info, host_only=None):
    if host_only:
        return Connection(host_only)
    if 'parallel' in decorators_info.keys():
        connection = ThreadingGroup(*decorators_info['hosts'])
    else:
        if 'hosts' in decorators_info.keys():
            host = decorators_info['hosts'][0]
        else:
            host = 'localhost'
        if settings_holder.get('host_string', None):
            host = settings_holder['host_string']
        connection = Connection(host)
    return connection


def load_source(name, path):
    if not os.path.exists(path):
        return {}
    return vars(SourceFileLoader("mod", path).load_module())


def load_py(path):
    data = {}
    loading = load_source("mod", path)
    for key, value in loading.items():
        if key in function_mapping.keys():
            data[key] = value
    return data


def main():
    doc = """
    Pypers wrapper of fabric 2.*
    """
    configs = [{
        'name': ['-f'],
        'type': str,
        'dest': 'file',
        'default': 'fabfile.py',
    }, {
        'name': ['functions'],
        'type': str,
        'help': 'a list of function:arguments',
        'nargs': argparse.REMAINDER
    }, {
        'name': ['--list'],
        'dest': 'display_list',
        'help': 'prints the usable functions',
        'action': 'store_true',
        'default': False
    }
    ]

    args = build_command_parser(configs, doc)
    global loader
    loader = load_py(args.file)
    if args.display_list:
        print("Available functions:")
        for key in loader.keys():
            signature = inspect.signature(loader[key])
            print("   %s: %s" % (key, signature))
        return
    else:
        if args.functions is None:
            raise Exception("At least one function should be called")
        for func in args.functions:
            if ':' in func:
                tmp = func.split(':')
                name = tmp[0]
                args = ':'.join(tmp[1:])
                args = args.split(',')
            else:
                name = func
                args = []
            if not loader.get(name):
                raise Exception("Function not found")
            loader[name](*args)


if __name__ == '__main__':
    main()
