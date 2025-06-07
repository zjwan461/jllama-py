import subprocess
import webview
from flask import Flask

import py.config as config
from py.controller import api

server = None
js_api = api.Api()
app_name = config.get_app_name()


def start_dev_server():
    commands = 'cd ui && npm run serve'
    result = subprocess.Popen(commands, shell=True)
    print(f"输出:\n{result.stdout}")
    return True


if config.is_dev():
    print("dev")
    # start_dev_server()

    window = webview.create_window(app_name, url="http://localhost:8001/app/", js_api=js_api, width=1200, height=800,
                                   confirm_close=True,
                                   text_select=True)
elif config.is_prd():
    print("prd")
    server = Flask(__name__, static_folder="static", template_folder="template")
    window = webview.create_window(app_name, server=server, js_api=js_api, width=1200, height=800,
                                   confirm_close=True,
                                   text_select=True)
else:
    raise RuntimeError("不支持的运行模式类型:" + config.get_model())

# @server.route("/")
# def index():
#     return render_template("index.html")


if __name__ == '__main__':
    webview.start(http_server=True, debug=config.is_dev())
