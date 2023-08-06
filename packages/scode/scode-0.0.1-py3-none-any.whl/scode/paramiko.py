import time
import paramiko


def command(ssh: paramiko.SSHClient, query: str, timeout = None):
    """execute shell command

    Args:
        ssh (paramiko.SSHClient): paramiko ssh client
        query (str): shell command

    Returns:
        tuple[str, str]: stdout, stderr
    """
    
    stdin, stdout, stderr = ssh.exec_command(query, timeout=timeout)
    
    # Wait for the command to terminate
    while not stdout.channel.exit_status_ready():
        time.sleep(1)
    
    stdout_text = stdout.read().decode('utf-8').strip()
    err_text = stderr.read().decode('utf-8').strip()
    return stdout_text, err_text


def execute_sql_query(ssh: paramiko.SSHClient, user_id: str, user_pw: str, db_name: str, query: str) -> str:
    """execute sql query

    Args:
        ssh (paramiko.SSHClient): paramiko ssh client.
        user_id (str): ID to log in.
        user_pw (str): Password to log in.
        db_name (str): Name of the database to be connected to.
        query (str): query statement to execute.

    Returns:
        str: standard output of execution.
    """    
    query = query.replace('\'','\"')
    fquery = f"""mysql -u{user_id} -p{user_pw} {db_name} -e '{query}'"""
    return command(ssh, fquery)
