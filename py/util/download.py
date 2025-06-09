# 模型下载
from modelscope import snapshot_download


def download(model_name: str, cache_dir, file_pattern):
    model_dir = snapshot_download(model_name, cache_dir=cache_dir, allow_file_pattern=file_pattern)
    print(f"Model downloaded to {model_dir}")
