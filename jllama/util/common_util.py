import os
import subprocess
import sys

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
