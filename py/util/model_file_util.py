import json

import requests
from py.util.logutil import Logger

logger = Logger("Api.py")


def get_model_file(repo: str, revision="master", root=""):
    resp = requests.get(
        "https://modelscope.cn/api/v1/models/" + repo + "/repo/files?Revision=" + revision + "&Root=" + root)
    if resp.status_code == 200:
        dic = json.loads(resp.text)
        files = dic["Data"]["Files"]
        return files
    else:
        logger.warn(f"resp http status= {resp.status_code}")
    return None


for file in get_model_file("unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF", revision="master"):
    print(file)
