import subprocess
import webview
from flask import Flask, send_from_directory

import py.config as config
from py.controller import api

server = None
controller = api.Api()
app_name = config.get_app_name()


class JsApi:

    def __init__(self, control: api.Api):
        self.controller = control

    def open_file_select(self):
        return self.controller.open_file_select()

    def show_tips(self):
        return self.controller.show_tips()

    def get_nav(self):
        return self.controller.get_nav()

    def get_sys_info(self):
        return self.controller.get_sys_info()

    def init_env(self):
        return self.controller.init_env()

    def model_list(self, param):
        return self.controller.model_list(param)

    def create_model(self, params):
        return self.controller.create_model(params)

    def search_model_file(self, params):
        return self.controller.search_model_file(params)

    def delete_model(self, id):
        return self.controller.delete_model(id)

    def create_download(self, params):
        self.controller.create_download(params, window)
        return "success"

    def create_batch_download(self, params):
        self.controller.create_batch_download(params, window)
        return "success"

    def get_download_files(self, model_id):
        return self.controller.get_download_files(model_id)


js_api = JsApi(controller)


def start_dev_server():
    commands = 'cd ui && npm run serve'
    result = subprocess.Popen(commands, shell=True)
    print(f"输出:\n{result.stdout}")
    return True


if config.is_dev():
    print("dev")
    if config.get_value("auth_start_dev_server"):
        start_dev_server()
    window = webview.create_window(app_name, url="http://localhost:8001/app/", js_api=js_api,
                                   width=config.get_app_width(), height=config.get_app_height(),
                                   confirm_close=True,
                                   text_select=True)
elif config.is_prd():
    print("prd")
    server = Flask(__name__)
    window = webview.create_window(app_name, server=server, js_api=js_api, width=config.get_app_width(),
                                   height=config.get_app_height(),
                                   confirm_close=True,
                                   text_select=True)


    @server.route("/")
    def index():
        return send_from_directory("ui/dist", "index.html")

else:
    raise RuntimeError("不支持的运行模式类型:" + config.get_model())

if __name__ == '__main__':
    webview.start(http_server=True, debug=config.is_dev())
