import os
import subprocess
import sys
from io import BytesIO

import requests
from PIL import Image
from PIL.ImageFile import ImageFile
import signal

from jllama.util.logutil import Logger

logger = Logger(__name__)


def open_file(file_path) -> None:
    os.startfile(file_path)


def check_llamafactory_install() -> bool:
    llamafactory_cli_path = os.path.join(sys.exec_prefix, "Scripts/llamafactory-cli")
    """
    Check if llamafactory is installed.
    """
    try:
        result = subprocess.run(args=f"{llamafactory_cli_path} version", check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e)
        return False


# 加载输入图像（可以替换为本地图像）
def load_image(url_or_path) -> ImageFile:
    if url_or_path.startswith("http"):
        response = requests.get(url_or_path)
        return Image.open(BytesIO(response.content)).convert("RGB")
    else:
        return Image.open(url_or_path).convert("RGB")


def kill_process_by_pid(pid):
    """
    根据PID关闭程序

    Args:
        pid: 要关闭的进程ID

    Returns:
        bool: 操作是否成功
    """
    try:
        # 检查PID是否为整数
        pid = int(pid)

        if sys.platform.startswith('win32'):
            # Windows系统使用taskkill命令
            # /F 表示强制终止，/PID 指定进程ID
            result = os.system(f'taskkill /F /PID {pid}')
            return result == 0
        else:
            # Unix/Linux/macOS系统使用signal
            # 先尝试发送SIGTERM（15），允许进程优雅退出
            os.kill(pid, signal.SIGTERM)

            # 等待片刻，如果进程仍在运行则发送SIGKILL（9）强制终止
            import time
            time.sleep(0.5)

            try:
                # 检查进程是否仍在运行
                os.kill(pid, 0)  # 发送0信号不做任何操作，仅用于检查进程是否存在
                # 如果未抛出异常，说明进程仍在运行，强制终止
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass  # 进程已退出，无需进一步操作

            return True

    except ValueError:
        print(f"错误：{pid} 不是有效的进程ID")
        return False
    except OSError as e:
        print(f"操作失败：{e}")
        return False
    except Exception as e:
        print(f"发生未知错误：{e}")
        return False


def is_pid_running(pid):
    """
    判断指定PID的进程是否在运行

    Args:
        pid: 进程ID（整数或字符串）

    Returns:
        bool: 如果进程正在运行则返回True，否则返回False
        None: 如果输入的PID无效
    """
    try:
        # 转换PID为整数
        pid = int(pid)
        if pid <= 0:
            print("错误：PID必须是正整数")
            return None
    except ValueError:
        print(f"错误：'{pid}' 不是有效的PID")
        return None

    try:
        if sys.platform.startswith('win32'):
            # Windows系统：使用tasklist命令检查
            # 过滤指定PID并隐藏输出
            cmd = f'tasklist /FI "PID eq {pid}"'
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # 如果输出不为空，说明进程存在
            info = result.stdout.strip()
            return len(info) > 0 and "\n" in info
        else:
            # Unix/Linux/macOS系统：发送0号信号检查
            # 0号信号不会对进程产生实际影响，仅用于检测进程是否存在
            os.kill(pid, 0)
            return True
    except OSError:
        # 进程不存在或没有权限访问
        return False
    except Exception as e:
        print(f"检查过程中发生错误：{e}")
        return False
