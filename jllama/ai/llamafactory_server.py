import multiprocessing
from llamafactory.extras.misc import fix_proxy, is_env_enabled
from llamafactory.webui.interface import create_ui
from jllama.util.logutil import Logger
from jllama.util.common_util import open_file

logger = Logger(__name__)

webui_process = multiprocessing.Process()


def start_webui_process(host: str, port: int) -> None:
    global webui_process
    if webui_process.is_alive():
        open_file(f"http://127.0.0.1:{port}")
        raise Exception("llamafactory服务已在运行")

    webui_process = multiprocessing.Process(target=start_webui, args=(host, port))
    webui_process.start()


def stop_webui_process() -> None:
    global webui_process
    if webui_process.is_alive():
        webui_process.terminate()


def start_webui(host: str, port: int):
    gradio_share = is_env_enabled("GRADIO_SHARE")
    server_name = host
    logger.info(f"Visit http://ip:{port} for Web UI, e.g., http://127.0.0.1:{port}")
    fix_proxy(ipv6_enabled=False)
    create_ui().queue().launch(share=gradio_share, server_name=server_name, inbrowser=True, server_port=port)
