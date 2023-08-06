import logging
import os
from typing import Text

import paramiko
from fabric import Connection
from invoke.exceptions import CommandTimedOut

from .unix_path import join as unix_join

logger = logging.getLogger("ssh_client")


class SSHClient(object):
    """
    SSH client, you can use it to execute shell command and upload or download file with SFTP.
    """

    def __init__(self, host, user, passwd, working_dir=os.path.abspath(os.path.curdir), port=22) -> None:
        super().__init__()
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__connection = None
        self.__transport = None
        self.__sftp = None
        self.__working_dir = working_dir

    def connect(self) -> None:
        """
        Create SSH session.
        """
        self.__connection = Connection(host=self.__host, user=self.__user, connect_kwargs={"password": self.__passwd})
        self.__transport = paramiko.Transport((self.__host, self.__port))
        self.__transport.connect(username=self.__user, password=self.__passwd)
        self.__sftp = paramiko.SFTPClient.from_transport(self.__transport)

    def close(self) -> None:
        """
        Close SSH session.
        """
        if self.__connection:
            self.__connection.close()

        if self.__transport:
            self.__transport.close()

    @classmethod
    def callback(cls, transferred_bytes, total_bytes):
        print("\b\b\b\b\b\b\b%6.2f%%" % (transferred_bytes / total_bytes * 100,), end='')
        if transferred_bytes == total_bytes:
            print()

    def exec(self, cmd: Text, pty=False, timeout=None, ignore_timeout=False, ignore_exit=False) -> None:
        """
        Execute a command on remote.
        """
        logger.info('Command: [%s].', cmd)
        try:
            result = self.__connection.run(cmd, pty=pty, timeout=timeout, warn=ignore_exit)
            logger.info('Command[%s]:[%s], exit code: [%s].', self.__host, cmd, result.exited)
        except CommandTimedOut as e:
            if ignore_timeout:
                logger.warning('Execute Command Timeout: [%s].', cmd)
                return
            raise e

    def upload(self, local_path: Text, remote_directory: Text) -> None:
        """
        Upload file to remote directory.
        :param local_path: local file path.
        :param remote_directory: remote directory.
        """
        _, file_name = os.path.split(local_path)

        logger.info('Upload [%s] --> [%s:%s].', local_path, self.__host, remote_directory)
        self.__sftp.put(local_path, unix_join(remote_directory, file_name), callback=self.callback)

    def upload_working(self, file_name, remote_directory) -> None:
        """
        Upload file in working directory to remote directory.
        :param file_name: file name.
        :param remote_directory: remote directory.
        """
        full_path = os.path.join(self.__working_dir, file_name)
        self.upload(full_path, remote_directory)

    def upload_files(self, **kwargs):
        for file, target_path in kwargs.items():
            self.upload_working(os.path.join(self.__working_dir, file), target_path)

    def download(self, remote_path: Text, local_directory: Text):
        """
        Download file.
        :param remote_path: remote file path.
        :param local_directory: local directory.
        """
        _, file_name = os.path.split(remote_path)
        logger.info('Download [%s:%s] --> [%s].', self.__host, remote_path, local_directory)
        self.__sftp.get(remote_path, os.path.join(local_directory, file_name), callback=self.callback)

    def download_working(self, remote_path) -> None:
        """
        Download file to working directory.
        :param remote_path: remote file path.
        """
        self.download(remote_path, self.__working_dir)

    def download_files(self, *args):
        for file in args:
            self.download_working(file)
