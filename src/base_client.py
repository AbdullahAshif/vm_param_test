class BaseShellClient:
    def upload_file(self, local_path, remote_path):
        raise NotImplementedError

    def execute_command(self, command):
        raise NotImplementedError

    def check_file(self, remote_path, checksum):
        raise NotImplementedError
