# 模型下载
import os.path

from modelscope import snapshot_download as md_snapshot_download
from huggingface_hub import snapshot_download as hf_snapshot_download
from py.util.db_util import SqliteSqlalchemy, FileDownload, Model
from py.util.logutil import Logger
from py.config import get_proxy_config

logger = Logger("py.util.download.py")


def modelscope_download(model_id, model_repo: str, cache_dir, file_pattern, window=None):
    try:
        model_dir = md_snapshot_download(model_repo, cache_dir=cache_dir, allow_file_pattern=file_pattern)
        logger.info(f"Model downloaded to {model_dir}")
    except Exception as e:
        logger.error(e)
        if window:
            window.evaluate_js("vue.messageArrive('jllama提醒','文件下载失败','error')")
        return

    if model_dir != os.path.join(cache_dir, model_repo):
        session = SqliteSqlalchemy().session
        try:
            file_list = session.query(FileDownload).filter(FileDownload.model_id == model_id).filter(
                FileDownload.file_name.in_(file_pattern)).all()
            for file in file_list:
                file.file_path = os.path.join(model_dir, file.file_name)
            model = session.query(Model).get(model_id)
            model.save_dir = model_dir
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
        finally:
            session.close()

    if window:
        content = ""
        for item in file_pattern:
            content += item + "; "
        content += '已下載'
        window.evaluate_js("vue.messageArrive('jllama提醒','" + content + "','success')")


def huggingface_download(model_id, model_repo: str, cache_dir, file_pattern, window=None):
    proxy_config = get_proxy_config()
    if proxy_config is not None:
        http_proxy = proxy_config.get("http_proxy")
        if http_proxy and len(http_proxy) > 0:
            os.environ["http_proxy"] = http_proxy
        https_proxy = proxy_config.get("https_proxy")
        if https_proxy and len(https_proxy) > 0:
            os.environ["https_proxy"] = https_proxy

    try:
        model_dir = hf_snapshot_download(model_repo, cache_dir=cache_dir, allow_patterns=file_pattern)
        logger.info(f"Model downloaded to {model_dir}")
    except Exception as e:
        logger.error(e)
        if window:
            window.evaluate_js("vue.messageArrive('jllama提醒','文件下载失败','error')")
        return

    session = SqliteSqlalchemy().session
    try:
        file_list = session.query(FileDownload).filter(FileDownload.model_id == model_id).filter(
            FileDownload.file_name.in_(file_pattern)).all()
        for file in file_list:
            file.file_path = os.path.join(model_dir, file.file_name)
        model = session.query(Model).get(model_id)
        model.save_dir = model_dir
        session.commit()
    except Exception as e:
        logger.error(e)
        session.rollback()
    finally:
        session.close()

    if window:
        content = ""
        for item in file_pattern:
            content += item + "; "
        content += '已下載'
        window.evaluate_js("vue.messageArrive('jllama提醒','" + content + "','success')")
