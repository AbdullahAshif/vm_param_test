import paramiko


class SSHClient:
    def __init__(self, host, username, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=username, password=password)

    def upload_file(self, local_path, remote_path):
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode('utf-8') + stderr.read().decode('utf-8')

    def check_file(self, remote_path, local_checksum):
        checksum_command = f"sha256sum {remote_path} | awk '{{print $1}}'"
        remote_checksum = self.execute_command(checksum_command).strip()
        if remote_checksum == local_checksum:
            return remote_checksum
        return None

    def close(self):
        self.client.close()
