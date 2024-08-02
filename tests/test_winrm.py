# This is to check if the local host can connect with VM and print its dir list
import paramiko
import winrm


def connect_winrm(host, username, password):
    session = winrm.Session(host, auth=(username, password), transport='basic', server_cert_validation='ignore')
    return session


# Define a test function
def test_winrm_connection():
    host = "http://192.168.0.187:5985/wsman"
    username = "a.moinur"
    password = "Ws310892"

    session = connect_winrm(host, username, password)
    result = session.run_cmd('dir')
    output = result.std_out.decode()

    # Check that the output is not empty (for demonstration purposes)
    assert output, "Command output is empty"
    print(output)


def connect_ssh(host, port, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, port=port, username=username, password=password)
    return ssh_client


# Define a test function
def test_ssh_connection():
    host = "192.168.0.157"
    port = 22  # Default SSH port
    username = "amoinur"
    password = "Ws310892"

    ssh_client = connect_ssh(host, port, username, password)
    stdin, stdout, stderr = ssh_client.exec_command('ls -l')  # Using 'ls -l' for a detailed directory list
    output = stdout.read().decode()

    # Check that the output is not empty (for demonstration purposes)
    assert output, "Command output is empty"
    print(output)

    ssh_client.close()


# Run the test
test_ssh_connection()
