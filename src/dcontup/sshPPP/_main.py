import paramiko


class SSHPPP:
    def __init__(self, host, user, password, port=22):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, self.port, self.user, self.password)

    def exec_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read().decode().strip(), stderr.read().decode().strip()

    def close(self):
        self.ssh.close()
