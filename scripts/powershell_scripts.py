# scripts/powershell_scripts.py

def create_directory_script(directory):
    return f"""
    if (-not (Test-Path -Path "{directory}")) {{
        New-Item -Path "{directory}" -ItemType Directory -Force
        Write-Output "Directory created: {directory}"
    }} else {{
        Write-Output "Directory already exists: {directory}"
    }}
    """


def upload_file_script(encoded_content, remote_path):
    return f"""
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


def file_exists_check_script(path):
    return f"Test-Path -Path '{path}'"


def get_file_checksum_script(remote_path):
    return f"""
    if (Test-Path -Path "{remote_path}") {{
        $checksum = Get-FileHash -Path "{remote_path}" -Algorithm SHA256
        $checksum.Hash
    }} else {{
        throw "File does not exist: {remote_path}"
    }}
    """
