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


def get_db_config():
    return DbConfig(dic.get("db"))


def get_log_config():
    return LogConfig(dic.get("log"))


class DbConfig:

    def __init__(self, kwargs: dict):
        self.url = kwargs.get("url")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.database = kwargs.get("database")

    def get_url(self):
        return self.url

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_database(self):
        return self.database


class LogConfig:

    def __init__(self, kwargs: dict):
        self.path = kwargs.get("path")

    def get_path(self):
        return self.path


if __name__ == '__main__':
    print(is_dev())
