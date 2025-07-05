import subprocess
import sys
from jllama.util.logutil import Logger

logger = Logger(__name__)


def install_package(package_name):
    try:
        # 使用 sys.executable 确保调用当前 Python 环境的 pip
        with subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "-i", "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple",
                 package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
        ) as proc:
            for line in proc.stdout:
                yield f"{line.strip()}\n"
    except subprocess.CalledProcessError as e:
        logger.error(e)
        yield f"安装失败: {e.stderr}"

# 示例：安装 requests 包
# install_package("requests")
