import logging
import logging.config
import os
import py.config as config

log_path = config.get_log_config().get_path()
if not os.path.exists(log_path):
    os.mkdir(log_path)

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "logging.conf")
logging.config.fileConfig(file_path)


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
