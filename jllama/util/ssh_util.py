import os.path

import paramiko
from scp import SCPClient  # 需额外安装：pip install scp
from jllama.util.logutil import Logger

logger = Logger(__name__)


def upload_and_exec(hostname: str, port: int, username: str, password: str, local_script_path: str,
                    remote_script_dir: str, exe_path: str):
    # 建立 SSH 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_script_dir}")
        err_output = stderr.read().decode()
        if err_output != "":
            e = ValueError(f"无法创建远程目录,{err_output}")
            logger.error(e)
            raise e

        script_name = os.path.basename(local_script_path)
        # 通过 SCP 上传文件
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_script_path, remote_path=remote_script_dir)  # 上传到远程目录

        # 执行远程临时脚本
        stdin, stdout, stderr = ssh.exec_command(f"{exe_path} {remote_script_dir}/{script_name}")

        i = 0
        for line in iter(stdout.readline, ''):
            if i == 0:
                yield "remote-train: info start"
            yield "remote-train: " + line.strip()
            i += 1
        else:
            yield "remote-train: info finish"

        i = 0
        for line in iter(stderr.readline, ''):
            if i == 0:
                yield "remote-train: error start"
            yield "remote-train: " + line
            i += 1
        else:
            yield "remote-train: error finish"


    except Exception as e:
        logger.error(e)
    finally:
        ssh.close()


def check_connection(hostname: str, port: int, username: str, password: str):
    # 建立 SSH 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command("ls")
        logger.info(f"ls exec result: {stdout.read().decode()}")
        logger.info(f"连接成功")
        ssh.close()
        return True
    except Exception as e:
        logger.error(e)
        return False
