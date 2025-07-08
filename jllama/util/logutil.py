import logging
import logging.config
import os
from pathlib import Path

log_file_dir = os.path.join(os.path.expanduser('~'), "jllama/logs")
path = Path(log_file_dir)
path.mkdir(exist_ok=True)
log_file_path = log_file_dir + "/jllama.log"
logging_conf_path = str(Path(__file__).parent.parent / "logging.conf")
with open(logging_conf_path, "r+", encoding="utf-8") as f:
    content = f.read()
    content = content.format(log_file_path)
    f.seek(0)
    f.write(content)
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
