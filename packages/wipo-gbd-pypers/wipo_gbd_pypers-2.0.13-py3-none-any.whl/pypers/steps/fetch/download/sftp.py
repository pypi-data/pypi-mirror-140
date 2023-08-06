import paramiko
import getpass
from pypers.steps.fetch.download.sftp_pk import SFTP_PK


class SFTP(SFTP_PK):

    def connect(self):
        # getting files from sftp
        self.sftp_params = self.fetch_from['from_sftp']
        self.logger.info('getting %s files from sftp %s %s' % (
            'all' if self.limit == 0 else self.limit,
            self.sftp_params['sftp_server'],
            self.sftp_params['sftp_dir']))
        if 'sftp_proxy' in self.sftp_params:
            proxy = paramiko.proxy.ProxyCommand(
                'nc --proxy %(proxy)s --proxy-type http %(host)s %(port)s' % {
                    'proxy': self.sftp_params.get('sftp_proxy'),
                    'host': self.sftp_params['sftp_server'],
                    'port': self.sftp_params.get('sftp_port', 22)})
            self.ssh = paramiko.Transport(proxy)
            self.ssh.connect(username=self.sftp_params['sftp_user'],
                             password=self.sftp_params['sftp_password'])
            sftp = paramiko.SFTPClient.from_transport(self.ssh)
            sftp.chdir(self.sftp_params['sftp_dir'])
            return sftp
        else:
            self.ssh = paramiko.SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.connect(self.sftp_params['sftp_server'],
                             username=self.sftp_params['sftp_user'],
                             password=self.sftp_params['sftp_password'])
            return self.ssh.open_sftp()

