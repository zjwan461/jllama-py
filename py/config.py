import json
import os

dic: dict


def read_config():
    global file_path, dic
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "config.json")
    f = open(file_path, "r")
    conf = f.read()
    dic = json.loads(conf)
    f.close()


read_config()


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


def get_ai_config() -> dict:
    return dic.get("ai_config")


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


def save_ai_config(config: dict):
    dic["ai_config"] = config
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)
    # reload config
    read_config()


def get_proxy_config() -> dict:
    return dic.get("proxy")


def save_proxy_config(config: dict):
    dic["proxy"] = config
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)
    # reload config
    read_config()
