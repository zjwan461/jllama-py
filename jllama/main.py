import subprocess
from flask_cors import CORS
import threading

import webview
from flask import Flask, send_from_directory, request, jsonify, Response

import jllama.config as config
from jllama.controller import api
from jllama.util.db_util import SqliteSqlalchemy, Model, FileDownload
import jllama.ai.reasoning_service as reasoning
import jllama.ai.llama_server as llama_server
import jllama.ai.llamafactory_server as llamafactory_server

controller = api.Api()
app_name = config.get_app_name()


class JsApi:

    def __init__(self, control: api.Api):
        self.controller = control

    def show_tk(self):
        return self.controller.show_tk()

    def open_file_select(self):
        return self.controller.open_file_select(window)

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

    def list_quantize_params(self):
        return self.controller.list_quantize_params()

    def quantize(self, params):
        return self.controller.quantize(params, window)

    def convert_hf_to_gguf(self, params):
        return self.controller.convert_hf_to_gguf(params, window)

    def list_covert_model(self, params):
        return self.controller.list_covert_model(params)

    def get_setting(self):
        return self.controller.get_setting()

    def save_setting(self, params):
        self.controller.save_setting(params)
        return "success"

    def get_llama_cpp_config(self):
        return self.controller.get_llama_cpp_config()

    def save_llama_cpp_config(self, content):
        self.controller.save_llama_cpp_config(content)
        return "success"

    def get_llama_server_info(self):
        return self.controller.get_llama_server_info()

    def start_llama_server(self):
        self.controller.start_llama_server()
        return "success"

    def stop_llama_server(self):
        self.controller.stop_llama_server()
        return "success"

    def open_file_in_sys_edit(self, file_path):
        self.controller.open_file_in_sys_edit(file_path)
        return "success"

    def train(self, params):
        return self.controller.train(params, window)

    def get_train_list(self, page, limit):
        return self.controller.get_train_list(page, limit)

    def delete_train_record(self, id):
        self.controller.delete_train_record(id)
        return "success"

    def generate_train_code(self, params):
        return self.controller.generate_train_code(params)

    def check_ssh_connection(self, hostname, port, username, password):
        return self.controller.check_ssh_connection(hostname, port, username, password)

    def remote_train(self, params):
        return self.controller.remote_train(params)

    def get_llamafactory_info(self):
        return self.controller.get_llamafactory_info()

    def install_llamafactory(self):
        return self.controller.install_llamafactory()

    def install_llamafactory_manual(self):
        return self.controller.install_llamafactory_manual()

    def reload_install_state(self):
        return self.controller.reload_install_state()

    def is_training(self):
        return self.controller.is_training()

    def stop_train(self):
        return self.controller.stop_train()

    def get_ai_chat_url(self):
        return self.controller.get_ai_chat_url()

    def start_lf_webui(self):
        return self.controller.start_lf_webui()

    def stop_lf_webui(self):
        return self.controller.stop_lf_webui()

    def is_lf_running(self):
        return self.controller.is_lf_running()

    def get_recent_server_info(self):
        return self.controller.get_recent_server_info()

    def get_sd_info(self):
        return self.controller.get_sd_info()

    def init_sd(self):
        return self.controller.init_sd(window)

    def sd_generate_pic(self, params):
        return self.controller.sd_generate_pic(params, window)

    def save_image(self, img_base64):
        return self.controller.save_image(img_base64,window)
server = Flask(__name__, static_folder="ui/dist", static_url_path="/")

CORS(server)

server_config = config.get_server_config()

js_api = JsApi(controller)


def start_dev_server():
    commands = 'cd ui && npm run serve'
    result = subprocess.Popen(commands, shell=True)
    print(f"输出:\n{result.stdout}")
    return True


if config.is_dev():
    print("dev")
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
    gguf_file = None
    if model is None:
        gguf_file = session.query(FileDownload).filter(FileDownload.file_path == model_name).first()
        if gguf_file is None:
            return jsonify({"error": {"message": "Model not found"}}), 400
        else:
            model = session.query(Model).get(gguf_file.model_id)
    else:
        if data.get("fileId") is not None and isinstance(data.get("fileId"), int):
            gguf_file = session.query(FileDownload).get(data.get("fileId"))

    session.close()
    # 验证参数
    if not messages:
        return jsonify({"error": {"message": "Missing messages"}}), 400

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
    # 如果模型还没启动，先启动
    if model.id not in reasoning.running_llama and model.id not in reasoning.running_transformers:
        reasoning.run_reasoning(model, gguf_file, **generate_params)

    if model.type == "gguf":
        if data.get("stream"):
            return Response(reasoning.running_llama[model.id].chat_stream(messages),
                            headers={
                                'Content-Type': 'text/event-stream',
                                'Cache-Control': 'no-cache',
                            })
        else:
            return reasoning.running_llama[model.id].chat_blocking(messages), 200
    elif model.type == "hf":
        if data.get("stream"):
            return Response(reasoning.running_transformers[model.id].chat_stream(messages),
                            headers={
                                'Content-Type': 'text/event-stream',
                                'Cache-Control': 'no-cache',
                            })
        else:
            return reasoning.running_transformers[model.id].chat_blocking(messages), 200
    else:
        return jsonify({"error": {"message": f"not supported model type {model.type}"}}), 400


def start_dev_flask():
    server.run(port=server_config.get("port", 5000))


clean_count = 0


def before_show():
    global clean_count
    print("before_show")
    # 第一次加载窗口时，停止所有正在运行的模型
    if clean_count == 0:
        controller.stop_all_running_model()
    clean_count += 1


def stop_process():
    llama_server.stop_llama_server()
    llamafactory_server.stop_webui_process()


def main():
    # 加载页面的监听
    window.events.loaded += before_show
    window.events.closed += stop_process

    if config.is_dev():
        threading.Thread(target=start_dev_flask, daemon=True).start()
        webview.start(debug=True)
    else:
        webview.start(http_server=True, debug=False, http_port=server_config.get("port", 5000))


if __name__ == '__main__':
    main()
