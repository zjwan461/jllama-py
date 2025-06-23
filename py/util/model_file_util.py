import json

import requests
from py.util.logutil import Logger
import os
from py.config import get_proxy_config

logger = Logger("Api.py")


def get_modelscope_model_file(repo: str, revision="master", root=""):
    resp = requests.get(
        "https://modelscope.cn/api/v1/models/" + repo + "/repo/files?Revision=" + revision + "&Root=" + root)
    if resp.status_code == 200:
        dic = json.loads(resp.text)
        files = dic["Data"]["Files"]
        return files
    else:
        logger.warn(f"resp http status= {resp.status_code}")
    return None


# for file in get_model_file("unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF", revision="master"):
#     print(file)

def get_huggingface_model_file(repo: str):
    proxy_config = get_proxy_config()
    if proxy_config is not None:
        http_proxy = proxy_config.get("http_proxy")
        if http_proxy:
            os.environ["http_proxy"] = http_proxy
        https_proxy = proxy_config.get("https_proxy")
        if https_proxy:
            os.environ["https_proxy"] = https_proxy

    resp = requests.get(
        "https://huggingface.co/api/models/" + repo + "/revision/main?expand[]=siblings")
    if resp.status_code == 200:
        dic = json.loads(resp.text)
        files = dic["siblings"]
        result = []
        for file in files:
            item = {"Name": file.get('rfilename')}
            result.append(item)
        return result
    else:
        logger.warn(f"resp http status= {resp.status_code}")
    return None
