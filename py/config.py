import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "config.json")
f = open(file_path, "r")
conf = f.read()
dic = json.loads(conf)
f.close()


def get_value(key: str):
    return dic[key]


def get_app_name():
    return dic["app_name"]


def get_model():
    return dic.get("model")


def is_dev():
    return get_model() == "dev"


def is_prd():
    return get_model() == "prd"


def get_log_config():
    return LogConfig(dic.get("log"))


def get_app_height():
    return dic.get("app_height")


def get_app_width():
    return dic.get("app_width")

def get_db_url():
    return dic.get("db_url")


class LogConfig:

    def __init__(self, kwargs: dict):
        self.path = kwargs.get("path")

    def get_path(self):
        return self.path


if __name__ == '__main__':
    print(is_dev())
