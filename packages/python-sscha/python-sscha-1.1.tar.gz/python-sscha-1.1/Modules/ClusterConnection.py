import subprocess
import sys, os
import paramiko


class ClusterConnection:

    def __init__(self, hostname = None, username = None, port = 22, password = None):
        """
        This is a cluster connection interface.
        It is a more advanced interface than the cluster one, that enables to directly connec
        """

        self.hostname = hostname
        self.username = username
        self.port = port
        self.password = password
        self.ssh_server = None

        # Here the specific interfaces for different cluster types
        self.get_jobs_command = None
        self.cancel_job_command = None
        self.submit_job_command = None

    def start_connection(self):
        self.ssh_server = paramiko.SSHClient()
        self.ssh_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_server.connect(self.hostname, self.port, self.username, self.password)

    def send_command(self, cmd, return_error = False):
        stdin, stdout, stderr = self.ssh_server.exec_command(cmd)
        
        if not return_error:
            return stdout.read()
        else:
            return stdout.read(), stderr.read()
