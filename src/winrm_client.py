import base64
import os
import winrm


class WinRMClient:
    def __init__(self, host, username, password):
        self.session = winrm.Session(host, auth=(username, password), transport='basic',
                                     server_cert_validation='ignore')

    def upload_file(self, local_path, remote_path):
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"The file {local_path} does not exist.")

        with open(local_path, 'rb') as file:
            content = file.read()
        encoded_content = base64.b64encode(content).decode('utf-8')

        # Create directory if it doesn't exist
        directory = os.path.dirname(remote_path)
        create_dir_script = f"""
        if (-not (Test-Path -Path "{directory}")) {{
            New-Item -Path "{directory}" -ItemType Directory -Force
            Write-Output "Directory created: {directory}"
        }} else {{
            Write-Output "Directory already exists: {directory}"
        }}
        """
        result = self.session.run_ps(create_dir_script)
        dir_creation_output = result.std_out.decode().strip()
        dir_creation_error = result.std_err.decode().strip()

        print(f"Directory creation result: {dir_creation_output}")
        if dir_creation_error:
            print(f"Directory creation error: {dir_creation_error}")

        # Verify the directory was created
        dir_check_script = f"Test-Path -Path '{directory}'"
        dir_exists_result = self.execute_command(dir_check_script).strip().lower()
        print(f"Directory exists check result: {dir_exists_result}")
        if dir_exists_result != "true":
            raise FileNotFoundError(f"Directory {directory} does not exist after creation.")

        # Upload the file
        upload_script = f"""
        try {{
            $content = [System.Convert]::FromBase64String("{encoded_content}")
            [System.IO.File]::WriteAllBytes("{remote_path}", $content)
            if (Test-Path "{remote_path}") {{
                Write-Output "Success"
            }} else {{
                Write-Output "Failed to write file to {remote_path}"
            }}
        }} catch {{
            Write-Output "Failed: $($_.Exception.Message)"
        }}
        """

        upload_result = self.session.run_ps(upload_script)
        upload_output = upload_result.std_out.decode().strip()
        upload_error = upload_result.std_err.decode().strip()

        print(f"Upload script result: {upload_output}")
        if upload_error:
            print(f"Error uploading file: {upload_error}")

        # Post-upload check
        file_exists_check = f"Test-Path -Path '{remote_path}'"
        file_exists_result = self.execute_command(file_exists_check).strip().lower()
        print(f"File exists check result: {file_exists_result}")
        if file_exists_result != "true":
            raise FileNotFoundError(f"File {remote_path} does not exist after upload.")

    def execute_command(self, command):
        print(f"Executing command: {command}")
        result = self.session.run_ps(command)
        output = result.std_out.decode().strip()
        error = result.std_err.decode().strip()
        print(f"Command output: {output}")
        if error:
            print(f"Command error: {error}")
        return output

    def check_file(self, remote_path, local_checksum):
        checksum_script = f"""
        $file = Get-Item -Path "{remote_path}"
        if ($file -ne $null) {{
            $checksum = Get-FileHash -Path "{remote_path}" -Algorithm SHA256
            $checksum.Hash
        }} else {{
            Write-Output "File does not exist"
        }}
        """
        result = self.session.run_ps(checksum_script)
        output = result.std_out.decode().strip()
        if "File does not exist" in output:
            return None
        return output

    def close(self):
        # WinRM sessions are stateless, so no close operation is needed
        pass
