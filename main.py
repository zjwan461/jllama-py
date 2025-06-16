import subprocess
import threading
from typing import List, Dict

import webview
from flask import Flask, send_from_directory, request, jsonify

import py.config as config
from py.controller import api

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

    def delete_model(self, params):
        self.controller.delete_model(params)
        return "success"

    def create_download(self, params):
        self.controller.create_download(params, window)
        return "success"

    def create_batch_download(self, params):
        self.controller.create_batch_download(params, window)
        return "success"

    def get_download_files(self, model_id):
        return self.controller.get_download_files(model_id)

    def delete_file_download(self, file_id):
        self.controller.delete_file_download(file_id)
        return "success"

    def import_file(self, params):
        self.controller.import_file(params)
        return "success"

    def file_list(self, params):
        model_id = params.get("modelId")
        gguf_only = params.get("ggufOnly", False)
        return self.controller.file_list(model_id, gguf_only)

    def get_model(self, model_id):
        return self.controller.get_model(model_id)

    def run_model(self, params):
        return self.controller.run_model(params)

    def list_running_model(self,params):
        return self.controller.list_running_model(params)

    def stop_running_model(self,exec_log_id):
        return self.controller.stop_running_model(exec_log_id)


js_api = JsApi(controller)
server = Flask(__name__, static_folder="ui/dist", static_url_path="/")


def start_dev_server():
    commands = 'cd ui && npm run serve'
    result = subprocess.Popen(commands, shell=True)
    print(f"输出:\n{result.stdout}")
    return True


if config.is_dev():
    print("dev")
    if config.get_value("auto_start_dev_server"):
        start_dev_server()
    window = webview.create_window(app_name, url="http://localhost:8001/", js_api=js_api,
                                   width=config.get_app_width(), height=config.get_app_height(),
                                   confirm_close=True,
                                   text_select=True)
elif config.is_prd():
    print("prd")
    window = webview.create_window(app_name, server, js_api=js_api, width=config.get_app_width(),
                                   height=config.get_app_height(),
                                   confirm_close=True,
                                   text_select=True)


    @server.route("/")
    def index():
        return send_from_directory("ui/dist", "index.html")
else:
    raise RuntimeError("不支持的运行模式类型:" + config.get_model())


@server.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json
    # 提取请求参数
    model = data.get("model", "llama-2-7b")
    messages = data.get("messages", [])
    temperature = data.get("temperature", 0.7)
    top_p = data.get("top_p", 0.95)
    top_k = data.get("top_k", 40)
    max_tokens = data.get("max_tokens", 512)
    stream = data.get("stream", False)
    stop = data.get("stop", [])

    # 验证参数
    if not messages:
        return jsonify({"error": {"message": "Missing messages"}}), 400

    # 构建提示词
    prompt = messages_to_prompt(messages, model)

    # 准备生成参数
    generate_params = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "stop": stop if isinstance(stop, list) else [stop] if stop else [],
        "stream": stream
    }
    # todo
    return jsonify({}), 200


# 解析消息历史，转换为提示词
def messages_to_prompt(messages: List[Dict[str, str]], model: str) -> str:
    """将消息历史转换为模型特定的提示词格式"""
    if "llama-2" in model:
        # Llama 2 聊天格式
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                prompt += f"<<SYS>>\n{content}\n<</SYS>>\n\n"
            elif role == "user":
                prompt += f"[INST] {content} [/INST]"
            elif role == "assistant":
                prompt += f" {content} "

        # 如果最后一条消息是用户消息，添加助手响应前缀
        if messages[-1]["role"] == "user":
            prompt += " "
        return prompt
    else:
        # 默认格式
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            prompt += f"{role}: {content}\n"
        return prompt


def start_dev_flask():
    server.run(port=5000)


if __name__ == '__main__':
    if config.is_dev():
        threading.Thread(target=start_dev_flask).start()
        webview.start(debug=True)
    else:
        webview.start(http_server=True, debug=False)
