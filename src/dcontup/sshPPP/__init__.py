from ._main import SSHPPP

__all__ = ['SSHPPP', 'ssh_exec_command']


def ssh_exec_command(host, user, password, command, port=22):
    ssh = None
    try:
        ssh = SSHPPP(host, user, password, port)
        return ssh.exec_command(command)
    except Exception as e:
        raise e
    finally:
        ssh.close()
