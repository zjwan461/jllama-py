import logging
import logging.config
import os
from pathlib import Path

if not os.path.exists("log"):
    os.mkdir("log")

logging_conf_path  = str(Path(__file__).parent.parent / "logging.conf")
logging.config.fileConfig(logging_conf_path)


class Logger:

    def __init__(self, *args):
        if args and args[0]:
            self.logger = logging.getLogger(args[0])
        else:
            self.logger = logging.getLogger()

    def info(self, msg):
        self.logger.info(msg=msg)

    def warn(self, msg):
        self.logger.warning(msg=msg)

    def error(self, e):
        logging.exception(e)
