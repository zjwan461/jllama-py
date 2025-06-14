# 模型下载
import os.path

from modelscope import snapshot_download
from py.util.db_util import SqliteSqlalchemy, FileDownload
from py.util.logutil import Logger

logger = Logger("Api.py")


def modelscope_download(model_name: str, cache_dir, file_pattern, window: None):
    try:
        model_dir = snapshot_download(model_name, cache_dir=cache_dir, allow_file_pattern=file_pattern)
        print(f"Model downloaded to {model_dir}")
    except Exception as e:
        logger.error(e)
        window.evaluate_js("vue.messageArrive('jllama提醒','文件下载失败','error')")
        return

    if model_dir != os.path.join(cache_dir, model_name):
        session = SqliteSqlalchemy().session
        file_list = session.query(FileDownload).filter(FileDownload.file_name.in_(file_pattern)).all()
        for file in file_list:
            file.file_path = os.path.join(model_dir, file.file_name)
        session.commit()

    if window:
        content = ""
        for item in file_pattern:
            content += item + "; "
        content += '已下載'
        window.evaluate_js("vue.messageArrive('jllama提醒','" + content + "','success')")
