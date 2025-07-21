import json
import multiprocessing
import os.path
import tempfile

from jllama.util.db_util import SqliteSqlalchemy, Model, FileDownload
from modelscope import snapshot_download
from jllama.config import get_ai_config
from jllama.util.modelscope_util import get_modelscope_model_file
from jllama.ai.llama_server import run_llama_server

config_template: dict = {
    "host": "0.0.0.0",
    "port": 8888,
    "models": []
}


def get_model_template():
    return {
        "model": "{0}",
        "model_alias": "{0}",
        "chat_format": None,
        "n_gpu_layers": -1,
        "offload_kqv": True,
        "n_threads": 1,
        "n_batch": 512,
        "n_ctx": 2048
    }


class ConsoleApi:
    def __init__(self):
        self.running_models = []
        self.config_file_path = f"{tempfile.gettempdir()}/llama_cpp_config.json"
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)
        with open(self.config_file_path, "w") as f:
            pass
        self.process = multiprocessing.Process(target=run_llama_server, daemon=False,
                                               kwargs={"config_file": self.config_file_path})

    def list_models(self):
        session = SqliteSqlalchemy().session
        model_list = session.query(Model).filter(Model.type == "gguf").all()
        data = [
            ["ID", "Name", "Size", "CreateAt"]
        ]
        for model in model_list:
            item = []
            file_list = model.files
            total_size = 0
            for file in file_list:
                total_size += file.file_size
            item.append(model.id)
            item.append(model.name)
            item.append(str(total_size))
            item.append(str(model.create_time))
            data.append(item)

        # 计算每列的最大宽度
        column_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]

        # 格式化输出
        for row in data:
            print("  ".join(str(cell).ljust(width) for cell, width in zip(row, column_widths)))

    def download_model(self, param):
        allow_file_pattern = ".*"
        if len(param) >= 2:
            model_name = param[0]
            allow_file_pattern = param[1]
        else:
            model_name = param[0]

        files = get_modelscope_model_file(model_name, allow_file_pattern=allow_file_pattern)
        if files is None or len(files) == 0:
            print(f"can not found gguf model file about: {param}")
            return False

        primary_file = files[0]
        save_dir = snapshot_download(model_name, cache_dir=get_ai_config().get("model_save_dir"),
                                     allow_file_pattern=allow_file_pattern)

        session = SqliteSqlalchemy().session
        try:
            model = session.query(Model).filter(Model.name == model_name).first()
            if model is None:
                model = Model(name=model_name, repo=model_name, type="gguf", download_platform="modelscope",
                              save_dir=save_dir, primary_gguf=save_dir + "/" + primary_file["Path"])
                session.add(model)
            else:
                model.repo = model_name
                model.save_dir = save_dir
                model.type = "gguf"
                model.download_platform = "modelscope"

            for file in files:
                file_download = session.query(FileDownload).filter(FileDownload.file_name == file["Name"]).filter(
                    FileDownload.model_id == model.id).first()
                if file_download is None:
                    file_download = FileDownload(file_name=file["Name"], file_path=save_dir + "/" + file["Path"],
                                                 file_size=file["Size"], model_id=model.id,
                                                 model_name=model.name, model_repo=model.repo, type="下载",
                                                 download_platform="modelscope")
                    session.add(file_download)
                else:
                    file_download.file_name = file["Name"]
                    file_download.file_path = save_dir + "/" + file["Path"]
                    file_download.file_size = file["Size"]
                    file_download.model_id = model.id
                    file_download.model_name = model.name
                    file_download.model_repo = model.repo
                    file_download.type = "下载"
                    file_download.download_platform = "modelscope"
            session.commit()
            return model
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def run_model(self, model_name):
        session = SqliteSqlalchemy().session
        model = session.query(Model).filter(Model.name == model_name).filter(Model.type == "gguf").first()
        if model is None:
            model = self.download_model([model_name])

        if model.primary_gguf is None:
            print(f"{model_name} has no primary gguf, use jllama-cli --primary $(gguf_file) to mark primary gguf")
            return False

        if model_name in self.running_models:
            print(f"{model_name} is running")
        else:
            self.add_modle_config(self.config_file_path, model_name, model.primary_gguf)
            if self.process.is_alive():
                self.process.terminate()
            self.process.start()
            self.running_models.append(model_name)

    def add_modle_config(self, full_file_path: str, model_name, gguf_file_path):
        model_template = get_model_template()
        model_template["model"] = model_template["model"].format(gguf_file_path)
        model_template["model_alias"] = model_template["model_alias"].format(model_name)
        with open(full_file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            if content and len(content) > 0:
                dic = json.loads(content)
                models = dic.get("models", [])
                models.append(model_template)
            else:
                dic = config_template
                models = dic.get("models", [])
                models.append(model_template)
            dic["models"] = models
            f.truncate(0)
            f.seek(0)
            json.dump(dic, f, ensure_ascii=False, indent=4)

    def stop_model(self, model_name):
        if model_name == "all" or model_name == "*":
            self.running_models.clear()
            self.process.terminate()
            return True

        session = SqliteSqlalchemy().session
        model = session.query(Model).filter(Model.name == model_name).filter(Model.type == "gguf").first()
        if model is not None and model_name in self.running_models:
            model_count = self.remove_model_config(self.config_file_path, model_name)
            if self.process.is_alive():
                self.process.terminate()
                self.running_models.remove(model_name)
                if model_count > 0:
                    self.process.start()
                    self.running_models.append(model_name)
            else:
                print(f"{model_name is not running}")

    def remove_model_config(self, config_file_path, model_name):
        with open(config_file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            if content and len(content) > 0:
                dic = json.loads(content)
                models = dic.get("models", [])
                for item in models:
                    if item["model_alias"] == model_name:
                        models.remove(item)
                        break
                f.truncate(0)
                f.seek(0)
                json.dump(dic, f, ensure_ascii=False, indent=4)
                return len(models)

    def ps_process(self):
        print("running models:")
        for item in self.running_models:
            print(item)

    def show_model_info(self, model_name):
        session = SqliteSqlalchemy().session
        try:
            model = session.query(Model).filter(Model.name == model_name).filter(Model.type == "gguf").first()
            if model is not None:
                data = [
                    ["ID", "Name", "CreateAt", "PrimayGGUF", "Files"]
                ]
                file_list = model.files
                file_content = ""
                for file in file_list:
                    file_content += file.file_name + ", size=" + str(file.file_size) + "; "

                data.append([str(model.id), model.name, str(model.create_time), model.primary_gguf, file_content])

                # 计算每列的最大宽度
                column_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]

                # 格式化输出
                for row in data:
                    print("  ".join(str(cell).ljust(width) for cell, width in zip(row, column_widths)))
            else:
                print(f"can not found model: {model_name}")
        finally:
            session.close()

    def get_space(self, count):
        space_text = ""
        for i in range(0, count):
            space_text += " "
        return space_text

    def mark_primary(self, param):
        model_name = param[0]
        gguf_file_name = param[1]
        try:
            session = SqliteSqlalchemy().session
            model = session.query(Model).filter(Model.name == model_name).first()
            file = session.query(FileDownload).filter(FileDownload.model_name == model_name).filter(
                FileDownload.file_name == gguf_file_name).first()

            if model is None:
                print(f"can not found model with name: {model_name}")
                return False
            if file is None:
                print(f"can not found gguf file with model: {model_name}, file: {gguf_file_name}")
                return False

            model.primary_gguf = file.file_path
            session.commit()
            print(f"success to mark model: {model_name}`s primay gguf: {gguf_file_name}")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


console_api = ConsoleApi()
