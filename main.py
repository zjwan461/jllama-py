import subprocess
from flask_cors import CORS
import threading
from typing import List, Dict

import webview
from flask import Flask, send_from_directory, request, jsonify, Response, stream_with_context

import py.config as config
from py.controller import api
from py.util.db_util import SqliteSqlalchemy, Model, FileDownload
import py.ai.reasoning as reasoning

controller = api.Api()
app_name = config.get_app_name()


class JsApi:

    def __init__(self, control: api.Api):
        self.controller = control

    def show_tk(self):
        return self.controller.show_tk()

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

    def list_running_model(self, params):
        return self.controller.list_running_model(params)

    def stop_running_model(self, exec_log_id):
        return self.controller.stop_running_model(exec_log_id)

    def list_running_model_history(self, params):
        return self.controller.list_running_model_history(params)

    def del_running_model(self, id):
        return self.controller.del_running_model(id)

    def split_merge_gguf(self, params):
        return self.controller.split_merge_gguf(params, window)

    def list_split_merge(self, params):
        return self.controller.list_split_merge(params)

    def list_quantize(self, params):
        return self.controller.list_quantize(params)


js_api = JsApi(controller)
server = Flask(__name__, static_folder="ui/dist", static_url_path="/")

CORS(server)


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
    model_name = data.get("model", "llama-2-7b")
    messages = data.get("messages", [])

    session = SqliteSqlalchemy().session
    model = session.query(Model).filter(Model.name == model_name).first()
    if model is None:
        gguf_file = session.query(FileDownload).filter(FileDownload.file_path == model_name).first()
        if gguf_file is None:
            return jsonify({"error": {"message": "Model not found"}}), 400
        else:
            model = session.query(Model).get(gguf_file.model_id)
    else:
        gguf_file = session.query(FileDownload).get(data.get("fileId"))
    # 验证参数
    if not messages:
        return jsonify({"error": {"message": "Missing messages"}}), 400

    # 构建提示词
    # prompt = messages_to_prompt(messages, model)

    # 准备生成参数
    generate_params = {
        "messages": messages,
        "ngl": data.get("ngl", 0),
        "threads": data.get("threads", -1),
        "ctxSize": data.get("ctxSize", 0),
        "temperature": data.get("temperature", 0.8),
        "top_k": data.get("top_k", 30),
        "top_p": data.get("top_p", 0.9),
        "stream": data.get("stream", False)
    }
    if model.type == "gguf":
        if model.id not in reasoning.running_llama:
            reasoning.run_reasoning(model, gguf_file, **generate_params)
            # file_path = gguf_file.file_path
            # file_id = gguf_file.id
            # if gguf_file is None:
            #     file_path = os.path.join(model.save_dir, model.repo)
            #
            # reasoning_exec_log = ReasoningExecLog(model_id=model_id, model_name=model.name, model_type=model.type,
            #                                       file_id=file_id, file_path=file_path,
            #                                       reasoning_args=json.dumps(params),
            #                                       start_time=datetime.now())
        if data.get("stream"):
            return Response(reasoning.running_llama[model.id].chat_stream(messages),
                            headers={
                                'Content-Type': 'text/event-stream',
                                'Cache-Control': 'no-cache',
                                'Connection': 'keep-alive'
                            })
        else:
            return reasoning.running_llama[model.id].chat_blocking(messages), 200
    else:
        print("not supported yet")
        pass


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


clean_count = 0


def before_show():
    global clean_count
    print("before_show")
    if clean_count == 0:
        controller.stop_all_running_model()
    clean_count += 1


if __name__ == '__main__':
    # 添加关闭的监听
    window.events.loaded += before_show

    if config.is_dev():
        threading.Thread(target=start_dev_flask).start()
        webview.start(debug=True)
    else:
        webview.start(http_server=True, debug=False)
