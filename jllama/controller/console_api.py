from jllama.util.db_util import SqliteSqlalchemy, Model, FileDownload
from modelscope import snapshot_download
from jllama.config import get_ai_config
from jllama.util.modelscope_util import get_modelscope_model_file


class ConsoleApi:
    def __init__(self):
        pass

    def list_models(self):
        session = SqliteSqlalchemy().session
        model_list = session.query(Model).filter(Model.type == "gguf").all()
        result = ""
        title = "ID\t\tName\t\tSize\t\tCreateAt"
        result += title + "\n"
        for model in model_list:
            file_list = model.files
            total_size = 0
            for file in file_list:
                total_size += file.file_size
            result += str(model.id) + "\t\t" + model.name + "\t\t" + str(total_size) + "\t\t" + str(
                model.create_time) + "\n"
        print(result)

    def download_model(self, param):
        allow_file_pattern = ".*"
        if len(param) >= 2:
            model_name = param[0]
            allow_file_pattern = param[1]
        else:
            model_name = param[0]
        save_dir = snapshot_download(model_name, cache_dir=get_ai_config().get("model_save_dir"),
                                     allow_file_pattern=allow_file_pattern)

        files = get_modelscope_model_file(model_name, allow_file_pattern=allow_file_pattern)

        session = SqliteSqlalchemy().session
        model = session.query(Model).filter(Model.name == model_name).first()
        if model is None:
            model = Model(name=model_name, repo=model_name, type="gguf", download_platform="modelscope",
                          save_dir=save_dir)
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
                file_download = FileDownload(file_name=file["Name"], file_path=save_dir + "/" + file["Name"],
                                             file_size=file["Size"], model_id=model.id,
                                             model_name=model.name, model_repo=model.repo, type="gguf",
                                             download_platform="modelscope")
                session.add(file_download)
            else:
                file_download.file_name = file["Name"]
                file_download.file_path = save_dir + "/" + file["Name"]
                file_download.file_size = file["Size"]
                file_download.model_id = model.id
                file_download.model_name = model.name
                file_download.model_repo = model.repo
                file_download.type = "gguf"
                file_download.download_platform = "modelscope"
        session.commit()


console_api = ConsoleApi()
