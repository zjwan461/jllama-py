import base64
import json
import os.path
import shutil
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from io import BytesIO
from pathlib import Path
from time import sleep
import webview

import jllama.ai.llama_server as llama_server

import jllama.util.systemInfo_util as sysInfoUtil

import jllama.ai.reasoning_service as reasoning
from jllama.tk import log_handler
from jllama.ext.convert_hf_to_gguf import covert as cover_hf
from jllama.util import common_util
from jllama.util.logutil import Logger
from jllama.util.db_util import SqliteSqlalchemy, SysInfo, Model, FileDownload, ReasoningExecLog, GgufSplitMerge, \
    Quantize, \
    ModelConvert, TrainLora, RemoteServer, StableDiffusionInfo
import jllama.config as config
import orjson
import jllama.util.model_file_util as model_file_util
from jllama.util.download import modelscope_download, huggingface_download
import jllama.tk.log_viewer as log_viewer
import jllama.util.llama_cpp_origin_util as cpp_origin_util
from jllama.ai.model_finetuning import train, torch_gc, is_training, reset_train_state, stop_train
from jinja2 import Template
from jllama.util.ssh_util import check_connection, upload_and_exec
import jllama.util.pip_util as pip_util
import jllama.ai.llamafactory_server as llamafactory_server
from jllama.env import jllama_version, factory_version, cpp_version
from modelscope import snapshot_download
from jllama.ai.sd_reasoning import supported_scheduler, list_schedulers, text_to_pic, pic_to_pic, ip_adapter_faceid_pic, \
    default_negative_prompt

logger = Logger(__name__)


class Api:
    root = None
    log_viewer = None

    def get_log_viewer(self):
        return self.log_viewer

    def __init__(self):
        tk_thread = threading.Thread(target=self.init_tk, name="tk thread", daemon=True)
        tk_thread.start()

    def set_window(self, window):
        self.window = window

    def init_tk(self):
        self.root = tk.Tk()
        self.log_viewer = log_viewer.TextViewer(self.root)
        self.root.withdraw()  # 隐藏主窗口
        self.root.mainloop()

    def show_tk(self):
        self.root.deiconify()

    def open_file_select(self, window):
        result = window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=True, file_types=("所有文件 (*.*)",)
        )
        return result

    def show_tips(self):
        return "today is a good day"

    def get_nav(self):
        nav_path = str(Path(__file__).parent.parent / "nav.json")
        with open(nav_path, "r", encoding="utf-8") as f:
            conf = f.read()
            json_data = json.loads(conf)
            return json_data

    def get_sys_info(self):
        server_config = config.get_server_config()
        result = {"cpu": sysInfoUtil.get_cpu_info(), "memory": sysInfoUtil.get_memory_info(),
                  "gpus": sysInfoUtil.get_gpu_info(),
                  "os": sysInfoUtil.get_os_info(), "jllamaInfo": sysInfoUtil.get_jllama_info(),
                  "base_url": f"http://{server_config.get('host')}:{server_config.get('port')}"}
        return orjson.dumps(result).decode("utf-8")

    def init_env(self):
        session = SqliteSqlalchemy().session
        result = session.query(SysInfo).all()
        if len(result) <= 0:
            try:
                os_info = sysInfoUtil.get_os_info()
                gpu_platform = "cuda" if sysInfoUtil.is_cuda_available() else "cpu"
                sys_info = SysInfo(id=999, os_arch=os_info['arch'], platform=os_info['os'], gpu_platform=gpu_platform,
                                   cpp_version=cpp_version, factory_version=factory_version,
                                   self_version=jllama_version)
                session.add(sys_info)
                session.commit()
                return "success"
            except Exception as e:
                logger.error(e)
                session.rollback()
                return "error"
            finally:
                session.close()
        else:
            return "no_need"

    def model_list(self, param):
        page = param.get('page')
        limit = param.get('limit')
        search = param.get('search')
        offset = (page - 1) * limit
        session = SqliteSqlalchemy().session
        result = {"page": page, "limit": limit}
        try:
            if search is None or len(search) == 0:
                total = session.query(Model).count()
                result["total"] = total
                record = session.query(Model).order_by(
                    Model.create_time.desc()).offset(
                    offset).limit(limit).all()
                r_list = []
                for item in record:
                    tmp = item.to_dic()
                    if item.files is not None:
                        tmp["files"] = [x.to_dic() for x in item.files]
                    r_list.append(tmp)
                result["record"] = r_list
            else:
                total = session.query(Model).filter(Model.name.like('%' + search + '%')).count()
                result["total"] = total
                record = session.query(Model).filter(Model.name.like('%' + search + '%')).order_by(
                    Model.create_time.desc()).offset(
                    offset).limit(limit).all()
                r_list = []
                for item in record:
                    r_list.append(item.to_dic())
                result["record"] = r_list
            return orjson.dumps(result).decode("utf-8")
        finally:
            session.close()

    def create_model(self, params):

        session = SqliteSqlalchemy().session

        model = session.query(Model).get(params.get("id"))
        model_type = params.get("type")
        if model_type is None or len(model_type) == 0:
            model_type = "gguf" if "gguf" in params.get("repo").lower() else "hf"

        download_platform = params.get('download_platform')
        save_dir = ""
        repo = params.get('repo')
        if download_platform == "modelscope":
            save_dir = config.get_ai_config()["model_save_dir"] + "/" + repo
        elif download_platform == "huggingface":
            save_dir = config.get_ai_config()["model_save_dir"] + "/models--" + repo.replace("/", "--")
        action = "insert"
        if model is None:
            model = Model(name=params.get('name'), repo=repo,
                          download_platform=download_platform,
                          save_dir=save_dir,
                          type=model_type)
        else:
            model.name = params.get('name')
            model.repo = params.get('repo')
            model.download_platform = params.get('download_platform')
            # model.save_dir = config.get_ai_config()["model_save_dir"] + "/" + params.get('repo')
            model.type = model_type
            action = "update"
        try:
            if action == "insert":
                session.add(model)
            session.commit()
            result = model.to_dic()
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def search_model_file(self, params):
        download_platform = params.get("download_platform")
        if download_platform == "modelscope":
            return model_file_util.get_modelscope_model_file(repo=params.get("repo"))
        elif download_platform == "huggingface":
            return model_file_util.get_huggingface_model_file(repo=params.get("repo"))
        else:
            raise Exception("not supported download platform")

    def delete_model(self, params):
        model_id = params.get("model_id")
        del_file = params.get("del_file")
        session = SqliteSqlalchemy().session
        try:
            record = session.query(Model).get(model_id)
            if record:
                file_query = session.query(FileDownload).filter(FileDownload.model_id == model_id)
                file_list = file_query.all()
                if len(file_list) > 0:
                    if del_file == True:
                        for file in file_list:
                            os.remove(file.file_path) if os.path.exists(file.file_path) else logger.warn(
                                f"can not found this file: {file.file_path}")
                    file_query.delete()
                session.delete(record)
                session.commit()
            else:
                logger.info(f"can not found model with id={id}")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def create_download(self, params, window=None):
        model_id = params.get("modelId")
        model_name = params.get("modelName")
        model_repo = params.get("modelRepo")
        file_name = params.get('fileName')
        download_platform = params.get("download_platform")
        if file_name == '.gitattributes':
            return "skip"
        file_size = params.get('fileSize')
        save_dir = config.get_ai_config()["model_save_dir"]
        full_file_name = save_dir + "/" + model_name + "/" + file_name
        file_entity = FileDownload(model_id=model_id, model_name=model_name, model_repo=model_repo, file_name=file_name,
                                   file_path=full_file_name,
                                   file_size=file_size, type="下载", download_platform=download_platform)
        session = SqliteSqlalchemy().session
        try:
            old = session.query(FileDownload).filter(FileDownload.file_name == file_name).filter(
                FileDownload.model_id == model_id).first()
            if old:
                old.model_id = model_id
                old.model_name = model_name
                old.file_size = file_size
            else:
                session.add(file_entity)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

        file_list = [file_name]

        target = modelscope_download
        if download_platform == "huggingface":
            target = huggingface_download

        process = threading.Thread(target=target,
                                   name="download",
                                   args=(model_id, model_repo, config.get_ai_config()["model_save_dir"], file_list,
                                         window))
        process.start()
        return file_list

    def create_batch_download(self, params, window=None):
        model_id = params.get("modelId")
        model_name = params.get("modelName")
        model_repo = params.get("modelRepo")
        file_list = params.get('fileList')
        download_platform = params.get("download_platform")
        for item in file_list:
            if item["fileName"] == '.gitattributes':
                file_list.remove(item)
        save_dir = config.get_ai_config()["model_save_dir"]
        file_name_list = []
        for file in file_list:
            file_name = file.get('fileName')
            file_size = file.get('fileSize')
            full_file_name = save_dir + "/" + model_name + "/" + file_name
            file_entity = FileDownload(model_id=model_id, model_name=model_name, model_repo=model_repo,
                                       file_name=file_name,
                                       file_path=full_file_name,
                                       file_size=file_size, type="下载", download_platform=download_platform)
            session = SqliteSqlalchemy().session
            try:
                old = session.query(FileDownload).filter(FileDownload.file_name == file_name).filter(
                    FileDownload.model_id == model_id).first()
                if old:
                    old.model_id = model_id
                    old.model_name = model_name
                    old.file_size = file_size
                else:
                    session.add(file_entity)
                session.commit()
            except Exception as e:
                logger.error(e)
                session.rollback()
                raise e
            finally:
                session.close()

            file_name_list.append(file_name)

        target = modelscope_download
        if download_platform == "huggingface":
            target = huggingface_download

        process = threading.Thread(target=target,
                                   name="download",
                                   args=(model_id, model_repo, config.get_ai_config()["model_save_dir"], file_name_list,
                                         window))
        process.start()
        return file_name_list

    def get_download_files(self, model_id):
        session = SqliteSqlalchemy().session
        model = session.query(Model).get(model_id)
        if model is None:
            raise Exception("找不到model_id=" + model_id + "的数据")

        record = session.query(FileDownload).filter(FileDownload.model_id == model_id).all()
        result = []
        for item in record:
            percent = "0%"
            if os.path.exists(item.file_path):
                current_size = os.path.getsize(item.file_path)
                percent = current_size / (item.file_size if item.file_size is not None else current_size)
                percent = f"{percent * 100:.2f}%"
            dic_item = item.to_dic()
            dic_item["percent"] = percent
            result.append(dic_item)
        return orjson.dumps(result).decode("utf-8")

    def delete_file_download(self, file_id):
        session = SqliteSqlalchemy().session
        file_entity = session.query(FileDownload).get(file_id)
        try:
            if file_entity is not None:
                file_path = file_entity.file_path
                os.remove(file_path) if os.path.exists(file_path) else logger.warn(f"找不到此文件{file_path}")
                session.delete(file_entity)
                session.commit()
            else:
                logger.info(f"can not found file download record with id={file_id}")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def import_file(self, params):
        model_id = params.get("model_id")
        file_path = params.get("file_path")
        for full_file_path in file_path:
            if not os.path.exists(full_file_path):
                raise Exception(f"{full_file_path} is not exist")

        session = SqliteSqlalchemy().session
        try:
            model = session.query(Model).get(model_id)
            if model is None:
                raise Exception(f"model_id={model_id} can not be found in db")

            for full_file_path in file_path:
                file_name = os.path.basename(full_file_path)
                file_size = os.path.getsize(full_file_path)
                file_entity = FileDownload(model_id=model_id, model_name=model.name, model_repo=model.repo,
                                           file_path=full_file_path,
                                           file_name=file_name,
                                           file_size=file_size,
                                           type="导入")
                session.add(file_entity)

            if len(file_path) > 0:
                model.save_dir = os.path.dirname(file_path[0])
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def file_list(self, model_id, gguf_only):
        session = SqliteSqlalchemy().session
        try:
            query = session.query(FileDownload).filter(FileDownload.model_id == model_id)
            if gguf_only:
                query = query.filter(FileDownload.file_name.like("%.gguf"))
            files = query.all()
            result = []
            for item in files:
                dict_item = item.to_dic()
                result.append(dict_item)
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def get_model(self, model_id):
        session = SqliteSqlalchemy().session
        try:
            model = session.query(Model).get(model_id)
            return orjson.dumps(model.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def run_model(self, params):
        file_download = None
        model_id = params.get("modelId")
        session = SqliteSqlalchemy().session
        try:
            model = session.query(Model).get(model_id)
            if model is None:
                raise Exception(f"model_id={model_id} can not be found in db")
            if model.type == "gguf":
                file_id = params.get("fileId")
                file_download = session.query(FileDownload).get(file_id)
                if file_download is None:
                    raise Exception(f"file_id={file_id} can not be found in db")
                if file_download.model_id != model_id:
                    raise Exception(f"file_id={file_id} is not belong to model_id={model_id}")

            reasoning.run_reasoning(model, file_download, **params)

            file_id = None
            if file_download is None:
                file_path = os.path.join(model.save_dir, model.repo)
            else:
                file_path = file_download.file_path
                file_id = file_download.id

            reasoning_exec_log = ReasoningExecLog(model_id=model_id, model_name=model.name, model_type=model.type,
                                                  file_id=file_id, file_path=file_path,
                                                  reasoning_args=json.dumps(params),
                                                  start_time=datetime.now())
            session.add(reasoning_exec_log)
            session.commit()
            return orjson.dumps(reasoning_exec_log.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def list_running_model(self, params):
        page = params.get("page")
        limit = params.get("limit")
        search = params.get('search')
        offset = (page - 1) * limit
        running_llama = reasoning.running_llama
        running_transformers = reasoning.running_transformers
        llama_keys = list(running_llama.keys())
        transformers_keys = list(running_transformers.keys())
        running_keys = llama_keys + transformers_keys
        session = SqliteSqlalchemy().session
        result = {}
        try:
            query = session.query(ReasoningExecLog).filter(ReasoningExecLog.model_id.in_(running_keys)).filter(
                ReasoningExecLog.model_name.like('%' + search + '%')).filter(ReasoningExecLog.stop_time.is_(None))
            total = query.count()
            result['total'] = total
            reason_exec_logs = query.order_by(ReasoningExecLog.create_time.desc()).offset(offset).limit(limit).all()
            record = [item.to_dic() for item in reason_exec_logs]
            result['record'] = record
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def stop_running_model(self, exec_log_id):
        session = SqliteSqlalchemy().session
        try:
            reasoning_exec_log = session.query(ReasoningExecLog).get(exec_log_id)
            reasoning.stop_reasoning(reasoning_exec_log.model_id)
            reasoning_exec_log.stop_time = datetime.now()
            session.commit()
            return "success"
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def stop_all_running_model(self):
        session = SqliteSqlalchemy().session
        try:
            session.query(ReasoningExecLog).filter(ReasoningExecLog.stop_time.is_(None)).update(
                {ReasoningExecLog.stop_time: datetime.now()})
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

        reasoning.stop_all_reasoning()

    def list_running_model_history(self, params):
        page = params.get("page")
        limit = params.get("limit")
        search = params.get("search")
        offset = (page - 1) * limit
        result = {}
        session = SqliteSqlalchemy().session
        query = session.query(ReasoningExecLog).filter(ReasoningExecLog.model_name.like("%" + search + "%"))
        total = query.count()
        result["total"] = total
        if total > 0:
            reason_exec_logs = query.order_by(ReasoningExecLog.create_time.desc()).offset(offset).limit(limit).all()
            record = [item.to_dic() for item in reason_exec_logs]
            result["record"] = record
        return orjson.dumps(result).decode("utf-8")

    def del_running_model(self, id):
        session = SqliteSqlalchemy().session
        try:
            reasoning_exec_log = session.query(ReasoningExecLog).get(id)
            if reasoning_exec_log is not None:
                session.delete(reasoning_exec_log)
            session.commit()
            return "success"
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def split_merge_gguf(self, params, window):
        input_file = params.get("input")
        output_file = params.get("output")
        options = params.get("options")
        async_exec = params.get("async")
        split_option = None
        split_param = None
        if options == "split":
            split_option = params.get("splitOption")
            split_param = params.get("splitParam")
            split_params = {}
            if len(split_param) > 0:
                split_params = {params.get("splitOption"): params.get("splitParam")}
            if async_exec:
                t = threading.Thread(target=self.split_show,
                                     args=(input_file, output_file, split_params, window))
                t.start()
            else:
                self.split_show(input_file, output_file, params, window)
        elif options == "merge":
            if async_exec:
                t = threading.Thread(target=self.merge_show, args=(input_file, output_file, window))
                t.start()
            else:
                self.merge_show(input_file, output_file, window)
        else:
            raise Exception(f"illegal options: {options}")

        session = SqliteSqlalchemy().session

        try:
            gguf_split_merge = GgufSplitMerge(option=options, input=input_file, output=output_file,
                                              split_option=split_option, split_param=split_param)
            session.add(gguf_split_merge)
            session.commit()
            return orjson.dumps(gguf_split_merge.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def split_show(self, input_file, output_file, params: dict, window):
        self.log_viewer.append_text("GGUF split:\n")
        for chunk in cpp_origin_util.split_gguf(input_file, output_file, params):
            self.log_viewer.append_text(chunk)
        else:
            window.evaluate_js("vue.messageArrive('jllama提醒','gguf split任务完成','success')")

    def merge_show(self, input_file, output_file, window):
        self.log_viewer.append_text("GGUF merge:\n")
        for chunk in cpp_origin_util.merge_gguf(input_file, output_file):
            self.log_viewer.append_text(chunk)
        else:
            window.evaluate_js("vue.messageArrive('jllama提醒','gguf merge任务完成','success')")

    def list_split_merge(self, params):
        page = params.get("page")
        limit = params.get("limit")
        offset = (page - 1) * limit
        result = {}
        session = SqliteSqlalchemy().session
        try:
            total = session.query(GgufSplitMerge).count()
            result["total"] = total
            gguf_split_merges = session.query(GgufSplitMerge).order_by(GgufSplitMerge.create_time.desc()).offset(
                offset).limit(limit).all()
            record = []
            for item in gguf_split_merges:
                record.append(item.to_dic())
            result["record"] = record
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def list_quantize(self, params):
        page = params.get("page")
        limit = params.get("limit")
        offset = (page - 1) * limit
        result = {}
        session = SqliteSqlalchemy().session
        try:
            total = session.query(Quantize).count()
            result["total"] = total
            quantizes = session.query(Quantize).order_by(Quantize.create_time.desc()).offset(
                offset).limit(limit).all()
            record = []
            for item in quantizes:
                record.append(item.to_dic())
            result["record"] = record
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def list_quantize_params(self):
        return cpp_origin_util.supported_q_type()

    def quantize(self, params, window):
        input = params.get("input")
        output = params.get("output")
        q_type = params.get("qType")
        async_exec = params.get("async", False)

        if async_exec:
            t = threading.Thread(target=self.show_quantize, args=(input, output, q_type, window))
            t.start()
        else:
            self.show_quantize(input, output, q_type, window)

        session = SqliteSqlalchemy().session
        try:
            quantize = Quantize(input=input, output=output, param=q_type)
            session.add(quantize)
            session.commit()
            return orjson.dumps(quantize.to_dic()).decode('utf-8')
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def show_quantize(self, input, output, q_type, window):
        self.log_viewer.append_text("GGUF quantize:\n")
        for chunk in cpp_origin_util.quantize(input, output, q_type):
            self.log_viewer.append_text(chunk)
        else:
            window.evaluate_js("vue.messageArrive('jllama提醒','gguf量化任务完成','success')")

    def convert_hf_to_gguf(self, params, window):
        input_dir = params.get("input")
        output = params.get("output")
        q_type = params.get("qType")
        async_exec = params.get("async", False)
        script_file = params.get("scriptFile")
        log_handler.textViewer = self.get_log_viewer()
        if async_exec:
            t = threading.Thread(target=self.show_covert, args=(input_dir, output, q_type, script_file, window))
            t.start()
        else:
            self.show_covert(input_dir, output, q_type, script_file, window)

        session = SqliteSqlalchemy().session
        try:
            model_covert = ModelConvert(input=input_dir, output=output, q_type=q_type, script_file=script_file)
            session.add(model_covert)
            session.commit()
            return orjson.dumps(model_covert.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def show_covert(self, input_dir, output, q_type, script_file, window):
        if script_file == "convert_hf_to_gguf.py":
            cover_hf(model=input_dir, outfile=output, outtype=q_type)
            window.evaluate_js("vue.messageArrive('jllama提醒','gguf转换任务完成','success')")

    def list_covert_model(self, params):
        page = params.get("page")
        limit = params.get("limit")
        offset = (page - 1) * limit

        result = {}
        session = SqliteSqlalchemy().session
        try:
            total = session.query(ModelConvert).count()
            result["total"] = total
            model_convert_list = session.query(ModelConvert).order_by(ModelConvert.create_time.desc()).offset(
                offset).limit(limit)
            record = []
            for item in model_convert_list:
                record.append(item.to_dic())
            result["record"] = record
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def get_setting(self):
        return {"ai_config": config.get_ai_config(), "proxy": config.get_proxy_config(),
                "aigc": config.get_aigc_config(), "auto_open_log_window": config.get_auto_open_log_window()}

    def save_setting(self, params):
        ai_config = params.get("ai_config")
        config.save_ai_config(ai_config)
        proxy = params.get("proxy")
        config.save_proxy_config(proxy)
        aigc = params.get("aigc")
        min_seed = aigc.get("min_seed")
        max_seed = aigc.get("max_seed")
        if min_seed >= max_seed:
            raise ValueError("种子数的范围最大值必须大于最小值")
        config.save_aigc_config(aigc)
        auto_open_log_window = params.get("auto_open_log_window", True)
        config.save_auto_open_log_window(auto_open_log_window)

    def get_llama_cpp_config(self):
        file_path = config.get_llama_server_config_path()
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(config.get_default_llama_server_config(), ensure_ascii=False, indent=4))
        result = {"file_path": file_path}
        with open(file_path, "r", encoding="utf-8") as f:
            conf = f.read()
            result["conf"] = conf
            return result

    def save_llama_cpp_config(self, content):
        file_path = config.get_llama_server_config_path()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_llama_server_info(self):
        state = "stop"
        try:
            server_process = llama_server.server_process
            if server_process.is_alive():
                state = "running"
        except Exception as e:
            logger.info("llama server is not running")

        config = json.loads(self.get_llama_cpp_config()["conf"])
        result = {"server_port": config["port"], "server_status": state}
        return result

    def start_llama_server(self):
        config_file_path = config.get_llama_server_config_path()
        if not os.path.exists(config_file_path):
            raise ValueError("找不到llama_server配置文件")
        llama_server.run_llama_server_async(config_file=config_file_path)
        time.sleep(10)

    def stop_llama_server(self):
        llama_server.stop_llama_server()
        time.sleep(10)

    def open_file_in_sys_edit(self, file_path):
        # current_dir = os.getcwd()
        # common_util.open_file(os.path.join(current_dir, "jllama/llama_cpp_config.json"))
        if not os.path.exists(file_path):
            raise ValueError(f"找不到文件: {file_path}")
        common_util.open_file(file_path)

    def msg_append(self, msg, window):
        window.evaluate_js("vue.msgAppend('" + msg + "')")

    def train(self, params, window):
        if is_training():
            raise ValueError("当前存在正在运行的训练任务")
        model_path = params.get("modelPath")
        torch_dtype = params.get("torchDtype")
        train_output_dir = params.get("trainOutputDir")
        lora_save_dir = params.get("loraSaveDir")
        fin_tuning_merge_dir = params.get("finTuningMergeDir")
        dataset_path = params.get("datasetPath")
        dataset_test_size = params.get("datasetTestSize")
        dataset_max_length = params.get("datasetMaxLength")
        num_train_epochs = params.get("numTrainEpochs")
        per_device_train_batch_size = params.get("perDeviceTrainBatchSize")
        learning_rate = float(params.get("learningRate"))
        lora_target = params.get("loraTarget")
        lora_dropout = params.get("loraDropout")
        bnb_config = params.get("bnbConfig")

        if not os.path.exists(model_path):
            raise ValueError("找不到模型目录")

        if not os.path.exists(dataset_path):
            raise ValueError("找不到数据集文件")

        datestr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if train_output_dir is None or len(train_output_dir) == 0:
            train_output_dir = "./train_" + datestr

        if lora_save_dir is None or len(lora_save_dir) == 0:
            lora_save_dir = "./lora_" + datestr

        if fin_tuning_merge_dir is None or len(fin_tuning_merge_dir) == 0:
            fin_tuning_merge_dir = "./final_" + datestr

        bnb_4bit = False
        bnb_8bit = False
        if bnb_config == "bnb_4bit":
            bnb_4bit = True
        elif bnb_config == "bnb_8bit":
            bnb_8bit = True

        if lora_target is not None and lora_target != '':
            if lora_target != 'all':
                try:
                    lora_target = json.loads(lora_target)
                except Exception as e:
                    logger.error(e)
                    raise ValueError("指定lora_target参数为具体layer层数格式错误,应为例: [\"q_proj\", \"v_proj\"]")

        log_handler.textViewer = self.get_log_viewer()
        result = "失败"
        train_use_time, merge_use_time, err_msg = None, None, None
        try:
            train_use_time, merge_use_time, break_train = train(model_path=model_path, torch_dtype=torch_dtype,
                                                                dataset_path=dataset_path,
                                                                train_output_dir=train_output_dir,
                                                                lora_save_dir=lora_save_dir,
                                                                fin_tuning_merge_dir=fin_tuning_merge_dir,
                                                                dataset_test_size=dataset_test_size,
                                                                dataset_max_length=dataset_max_length,
                                                                num_train_epochs=num_train_epochs,
                                                                per_device_train_batch_size=per_device_train_batch_size,
                                                                learning_rate=learning_rate, lora_target=lora_target,
                                                                lora_dropout=lora_dropout, bnb_4bit=bnb_4bit,
                                                                bnb_8bit=bnb_8bit,
                                                                logging_steps=config.get_ai_config().get(
                                                                    "train_log_step", 5)
                                                                )
            result = "成功" if not break_train else "中断"
            window.evaluate_js("vue.messageArrive('jllama提醒','训练任务执行成功','success')")
        except Exception as e:
            err_msg = str(e)
            window.evaluate_js("vue.messageArrive('jllama提醒','训练任务执行失败，请在训练历史页查看具体原因','error')")
            logger.error(e)
            torch_gc()
            raise e
        finally:
            reset_train_state()
            self.save_train_result(result, "local", train_use_time, merge_use_time, err_msg, params)

    def save_train_result(self, result, type, train_use_time, merge_use_time, err_msg, params):
        session = SqliteSqlalchemy().session
        try:
            train_lora = TrainLora(train_args=json.dumps(params), result=result, type=type, err_msg=err_msg,
                                   train_use_time=train_use_time,
                                   merge_use_time=merge_use_time)
            session.add(train_lora)
            session.commit()
            return orjson.dumps(train_lora.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
        finally:
            session.close()

    def get_train_list(self, page, limit):
        session = SqliteSqlalchemy().session
        result = {}
        try:
            total = session.query(TrainLora).count()
            trainLoraList = session.query(TrainLora).order_by(TrainLora.create_time.desc()).offset(
                (page - 1) * limit).limit(limit).all()
            record = []
            for item in trainLoraList:
                record.append(item.to_dic())
            result["total"] = total
            result["record"] = record
            return orjson.dumps(result).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_train_record(self, id):
        session = SqliteSqlalchemy().session
        try:
            train_lora = session.query(TrainLora).get(id)
            if train_lora is not None:
                session.delete(train_lora)
                session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def generate_train_code(self, params):
        bnb_config = params.get("bnbConfig")
        bnb_4bit = False
        bnb_8bit = False
        if bnb_config == "bnb_4bit":
            bnb_4bit = True
        elif bnb_config == "bnb_8bit":
            bnb_8bit = True
        params["bnb_4bit"] = bnb_4bit
        params["bnb_8bit"] = bnb_8bit

        lora_target = params.get("loraTarget")
        if lora_target is not None and lora_target != '':
            if lora_target != 'all':
                try:
                    lora_target = json.loads(lora_target)
                    params["lora_target"] = lora_target
                except Exception as e:
                    logger.error(e)
                    raise ValueError("指定lora_target参数为具体layer层数格式错误,应为例: [\"q_proj\", \"v_proj\"]")
            else:
                params["lora_target"] = "\'all\'"

        params["learningRate"] = float(params.get("learningRate"))

        temp_file_path = str(Path(__file__).parent.parent / "templates/model_finetuning.jinja")
        with open(temp_file_path, "r", encoding="utf-8") as f:
            template = Template(f.read())
            return template.render(params)

    def check_ssh_connection(self, hostname, port, username, password):
        return check_connection(hostname, int(port), username, password)

    def remote_train(self, params):
        if not self.check_ssh_connection(params.get("remoteIp"), params.get("remotePort"), params.get("remoteUser"),
                                         params.get("remotePassword")):
            raise ValueError("SSH连接失败")

        self.save_remote_info(params)

        train_code = self.generate_train_code(params)
        temp_dir = tempfile.gettempdir()
        date_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        local_code_path = os.path.join(temp_dir, f"train_{date_str}.py")
        with open(local_code_path, "w", encoding="utf-8") as f:
            f.write(train_code)
            f.flush()

        start_time = time.time()
        result = True
        for item in upload_and_exec(params.get("remoteIp"), int(params.get("remotePort")),
                                    params.get("remoteUser"),
                                    params.get("remotePassword"), local_code_path,
                                    params.get("remotePath"), params.get("execPath")):
            self.log_viewer.append_text(item)

        end_time = time.time()

        self.save_train_result("成功", "remote", end_time - start_time, None, None,
                               params)

        return result

    def save_remote_info(self, params):
        session = SqliteSqlalchemy().session
        try:
            remote_server = RemoteServer(ip=params.get("remoteIp"), port=params.get("remotePort"),
                                         username=params.get("remoteUser"),
                                         password=params.get("remotePassword"),
                                         remote_path=params.get("remotePath"), python_exec_path=params.get("execPath"))
            session.add(remote_server)
            session.commit()
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def get_llamafactory_info(self):
        factory_install = sysInfoUtil.get_jllama_info()["factory_install"]
        factory_port = config.get_ai_config()["llama_factory_port"]
        return {"factory_install": factory_install, "factory_port": factory_port}

    def install_llamafactory(self):
        session = SqliteSqlalchemy().session
        sys_info = session.query(SysInfo).get(999)
        if sys_info.factory_install == "已安装":
            raise ValueError("LLamaFactory已安装")
        current_dir = os.getcwd()
        llama_factory_install_package = os.path.join(current_dir, "ext/llamafactory-0.9.3-py3-none-any.whl")

        for log in pip_util.install_package(llama_factory_install_package):
            self.log_viewer.append_text(log)

        if common_util.check_llamafactory_install():
            sys_info.factory_install = "已安装"
            session.commit()
            session.close()
            return True
        else:
            return False

    def install_llamafactory_manual(self):
        current_dir = os.getcwd()
        llama_factory_install_package = os.path.join(current_dir, "ext/llamafactory-0.9.3-py3-none-any.whl")
        install_content = (
            f"<p>进入终端，cd到项目根目录下，并执行以下命令安装llamafactory</p>"
            f"<p><strong>pip install {llama_factory_install_package}</strong></p>"
        )
        return install_content

    def reload_install_state(self):
        session = SqliteSqlalchemy().session
        sys_info = session.query(SysInfo).get(999)
        if common_util.check_llamafactory_install():
            sys_info.factory_install = "已安装"
        else:
            sys_info.factory_install = "未安装"
        session.commit()
        session.close()

    def is_training(self):
        return is_training()

    def stop_train(self):
        return stop_train()

    def get_ai_chat_url(self):
        port = config.get_server_config().get("port", 5000)
        return f"http://127.0.0.1:{port}/v1/chat/completions"

    def start_lf_webui(self):
        ai_config = config.get_ai_config()
        llama_factory_host = ai_config.get("llama_factory_host", "0.0.0.0")
        llama_factory_port = ai_config.get("llama_factory_port", 7860)
        llamafactory_server.start_webui_process(llama_factory_host, llama_factory_port)
        sleep(10)

    def stop_lf_webui(self):
        llamafactory_server.stop_webui_process()

    def is_lf_running(self):
        return llamafactory_server.webui_process.is_alive()

    def get_recent_server_info(self):
        session = SqliteSqlalchemy().session
        record = session.query(RemoteServer).order_by(RemoteServer.create_time.desc()).limit(1).all()
        session.close()
        if record is not None and len(record) > 0:
            return orjson.dumps(record[0].to_dic()).decode("utf-8")
        else:
            return None

    def get_sd_info(self):
        session = SqliteSqlalchemy().session
        try:
            sd_info = session.query(StableDiffusionInfo).get(999)
            if sd_info is None:
                sd_info = StableDiffusionInfo(id=999)
                session.add(sd_info)
            session.commit()
            return orjson.dumps(sd_info.to_dic()).decode("utf-8")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()

    def init_sd(self, window):
        model_save_dir = config.get_ai_config().get("model_save_dir")
        model_dir = snapshot_download("AI-ModelScope/stable-diffusion-v1-5", cache_dir=model_save_dir,
                                      allow_file_pattern="*")

        session = SqliteSqlalchemy().session
        try:
            sd_info = session.query(StableDiffusionInfo).get(999)
            if sd_info is None:
                sd_info = StableDiffusionInfo(id=999)
            sd_info.main_model_path = model_dir
            sd_info.state = "已初始化"
            session.commit()
            window.evaluate_js("vue.messageArrive('jllama提醒','StableDiffusion环境初始化成功','success')")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.rollback()

    def sd_generate_pic(self, params, window):
        sd_info = self.check_sd_env()
        """
        seed: -1,
        checkpoint: null,
        lora: null,
        scheduler: 'Euler',
        num_inference_steps: 30,
        img_num: 2,
        img_height: 512,
        img_width: 512
        """
        seed = int(params.get("seed", -1))
        prompt = params.get("prompt")
        negative_prompt = params.get("negative_prompt")
        checkpoint = params.get("checkpoint")
        lora = params.get("lora")
        scheduler = params.get("scheduler")
        lora_alpha = float(params.get("lora_alpha"))
        guidance_scale = float(params.get("guidance_scale"))
        num_inference_steps = int(params.get("num_inference_steps"))
        img_num = int(params.get("img_num"))
        img_height = int(params.get("img_height"))
        img_width = int(params.get("img_width"))

        if prompt is None or len(prompt) == 0:
            raise ValueError("正向提示词必填")

        if checkpoint is not None and len(checkpoint) > 0 and not os.path.exists(checkpoint):
            raise ValueError(f"找不到checkpoint文件：{checkpoint}")

        if lora is not None and len(lora) > 0 and not os.path.exists(lora):
            raise ValueError(f"找不到lora文件：{lora}")

        if not supported_scheduler(scheduler):
            raise ValueError(f"不支持的采样器，必须是: {list_schedulers()}")

        if lora_alpha > 1.0:
            raise ValueError("lora_alpha为0-1的小数")

        log_handler.textViewer = self.get_log_viewer()
        aigc_config = config.get_aigc_config()
        images, seed = text_to_pic(sd_origin_model_path=sd_info.main_model_path,
                                   prompt=prompt,
                                   negative_prompt=negative_prompt,
                                   checkpoint_path=checkpoint,
                                   lora_path=lora,
                                   num_images=img_num,
                                   guidance_scale=guidance_scale,
                                   seed=seed,
                                   scheduler=scheduler,
                                   num_inference_steps=num_inference_steps,
                                   lora_alpha=lora_alpha,
                                   height=img_height,
                                   width=img_width,
                                   log_step=aigc_config.get("log_step", 5),
                                   min_seed=aigc_config.get("min_seed", 1),
                                   max_seed=aigc_config.get("max_seed", 9999999999)
                                   )

        window.evaluate_js("vue.messageArrive('jllama提醒','图片生成成功','success')")

        result = {"seed": seed}
        images_base64 = []
        for image in images:
            # 转换为 Base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
            images_base64.append(img_str)
        result["images"] = images_base64
        return result

    def check_sd_env(self) -> StableDiffusionInfo:
        session = SqliteSqlalchemy().session
        sd_info = session.query(StableDiffusionInfo).get(999)
        if sd_info is None or sd_info.state == '待初始化' or not os.path.exists(sd_info.main_model_path):
            raise Exception("SD环境尚未初始化")
        session.close()
        return sd_info

    def save_image(self, img_base64, window):
        date_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        result = window.create_file_dialog(
            webview.SAVE_DIALOG, directory='/', save_filename=f'sd_generate_{date_str}.png'
        )
        # 检查是否包含数据前缀（如 data:image/jpeg;base64,）
        if img_base64.startswith('data:'):
            # 分割前缀和实际的 Base64 数据
            prefix, data = img_base64.split(',', 1)
            img_base64 = data

        image_data = base64.b64decode(img_base64)

        if result:
            with open(result, "wb") as f:
                f.write(image_data)
            return "success"
        else:
            return "abort"

    def sd_pic_to_pic(self, params, window):
        sd_info = self.check_sd_env()
        """
        seed: -1,
        checkpoint: null,
        lora: null,
        scheduler: 'Euler',
        num_inference_steps: 30,
        img_num: 2,
        img_height: 512,
        img_width: 512
        """
        input_img = params.get("input_img")
        strength = float(params.get("strength", 0.5))
        seed = int(params.get("seed", -1))
        prompt = params.get("prompt")
        negative_prompt = params.get("negative_prompt")
        checkpoint = params.get("checkpoint")
        lora = params.get("lora")
        scheduler = params.get("scheduler")
        lora_alpha = float(params.get("lora_alpha"))
        guidance_scale = float(params.get("guidance_scale"))
        num_inference_steps = int(params.get("num_inference_steps"))
        img_num = int(params.get("img_num"))
        img_height = int(params.get("img_height"))
        img_width = int(params.get("img_width"))
        ip_adapter_model = params.get("ip_adapter_model")

        if input_img is None or len(input_img) == 0:
            raise ValueError("请选择图片")

        if strength > 1.0 or strength < 0:
            raise ValueError("变化率strength为0-1的小数")

        if prompt is None or len(prompt) == 0:
            raise ValueError("正向提示词必填")

        if checkpoint is not None and len(checkpoint) > 0 and not os.path.exists(checkpoint):
            raise ValueError(f"找不到checkpoint文件：{checkpoint}")

        if lora is not None and len(lora) > 0 and not os.path.exists(lora):
            raise ValueError(f"找不到lora文件：{lora}")

        if not supported_scheduler(scheduler):
            raise ValueError(f"不支持的采样器，必须是: {list_schedulers()}")

        if lora_alpha > 1.0 or lora_alpha < 0:
            raise ValueError("lora_alpha为0-1的小数")

        if ip_adapter_model and len(ip_adapter_model) > 0 and not os.path.exists(
                sd_info.ip_adapter_model_path + "/models/" + ip_adapter_model):
            raise ValueError(f"找不到ip_adapter_model文件：{ip_adapter_model}")

        input_image = common_util.load_image(input_img)
        input_image = input_image.resize((img_width, img_height))

        log_handler.textViewer = self.get_log_viewer()
        aigc_config = config.get_aigc_config()
        images, seed = pic_to_pic(sd_origin_model_path=sd_info.main_model_path,
                                  input_image=input_image,
                                  prompt=prompt,
                                  negative_prompt=negative_prompt,
                                  checkpoint_path=checkpoint,
                                  lora_path=lora,
                                  ip_adapter_path=sd_info.ip_adapter_model_path,
                                  ip_adapter_subfolder="models",
                                  ip_adapter_weight_name=ip_adapter_model,
                                  num_images=img_num,
                                  guidance_scale=guidance_scale,
                                  seed=seed,
                                  scheduler=scheduler,
                                  strength=strength,
                                  num_inference_steps=num_inference_steps,
                                  lora_alpha=lora_alpha,
                                  log_step=aigc_config.get("log_step", 5),
                                  min_seed=aigc_config.get("min_seed", 1),
                                  max_seed=aigc_config.get("max_seed", 9999999999)
                                  )

        window.evaluate_js("vue.messageArrive('jllama提醒','图片生成成功','success')")

        result = {"seed": seed}
        images_base64 = []
        for image in images:
            # 转换为 Base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
            images_base64.append(img_str)
        result["images"] = images_base64
        return result

    def init_ip_adapter(self, window):
        model_save_dir = config.get_ai_config().get("model_save_dir")
        model_dir = snapshot_download("AI-ModelScope/IP-Adapter", cache_dir=model_save_dir,
                                      allow_file_pattern="*")
        session = SqliteSqlalchemy().session
        try:
            sd_info = session.query(StableDiffusionInfo).get(999)
            if sd_info is None:
                sd_info = StableDiffusionInfo(id=999)
            sd_info.ip_adapter_model_path = model_dir
            sd_info.ip_adapter_state = "已初始化"
            session.commit()
            window.evaluate_js("vue.messageArrive('jllama提醒','IP-Adapter环境初始化成功','success')")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.rollback()

    def init_ip_adapter_faceid(self, window):
        model_save_dir = config.get_ai_config().get("model_save_dir")
        faceid_model_dir = snapshot_download("guaidao/IP-Adapter-FaceID", cache_dir=model_save_dir,
                                             allow_file_pattern="*")

        insightface_model_dir = snapshot_download("deepghs/insightface", cache_dir=model_save_dir,
                                                  allow_file_pattern="*")

        Path(f"{insightface_model_dir}/models").mkdir(exist_ok=True)
        shutil.copytree(f"{insightface_model_dir}/buffalo_l", f"{insightface_model_dir}/models/buffalo_l")
        shutil.copytree(f"{insightface_model_dir}/buffalo_s", f"{insightface_model_dir}/models/buffalo_s")

        image_encoder_model_dir = snapshot_download("laion/CLIP-ViT-H-14-laion2B-s32B-b79K", cache_dir=model_save_dir,
                                                    allow_file_pattern="*")

        session = SqliteSqlalchemy().session
        try:
            sd_info = session.query(StableDiffusionInfo).get(999)
            if sd_info is None:
                sd_info = StableDiffusionInfo(id=999)
            sd_info.ip_adapter_faceid_model_path = faceid_model_dir
            sd_info.insightface_model_path = insightface_model_dir
            sd_info.image_encoder_model_path = image_encoder_model_dir
            sd_info.ip_adapter_faceid_state = "已初始化"
            session.commit()
            window.evaluate_js("vue.messageArrive('jllama提醒','IP-Adapter-FaceId环境初始化成功','success')")
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise e
        finally:
            session.rollback()

    def get_ip_adapter_models(self):
        session = SqliteSqlalchemy().session
        sd_info = None
        try:
            sd_info = session.query(StableDiffusionInfo).get(999)
        except Exception as e:
            logger.error(e)
        finally:
            session.rollback()

        model_list = []
        if sd_info is not None:
            amp = sd_info.ip_adapter_model_path
            if os.path.exists(amp) and os.path.exists(f"{amp}/models"):
                base_dir = f"{amp}/models"
                for entry in os.listdir(base_dir):
                    if not os.path.isdir(os.path.join(base_dir, entry)):
                        model_list.append(entry)
        return model_list

    def sd_ip_adapter_faceid(self, params, window):
        sd_info = self.check_sd_env()
        if sd_info.ip_adapter_faceid_state != "已初始化":
            raise ValueError("IP-Adapter-FaceID环境未初始化")
        """
        seed: -1,
        checkpoint: null,
        lora: null,
        scheduler: 'Euler',
        num_inference_steps: 30,
        img_num: 2,
        img_height: 512,
        img_width: 512
        """
        input_img = params.get("input_img")
        seed = int(params.get("seed", -1))
        prompt = params.get("prompt")
        negative_prompt = params.get("negative_prompt")
        checkpoint = params.get("checkpoint")
        lora = params.get("lora")
        lora_alpha = float(params.get("lora_alpha"))
        guidance_scale = float(params.get("guidance_scale"))
        num_inference_steps = int(params.get("num_inference_steps"))
        img_num = int(params.get("img_num"))
        img_height = int(params.get("img_height"))
        img_width = int(params.get("img_width"))
        ip_adapter_faceid_model = params.get("ip_adapter_faceid_model")

        if input_img is None or len(input_img) == 0:
            raise ValueError("请选择图片")

        if prompt is None or len(prompt) == 0:
            raise ValueError("正向提示词必填")

        if checkpoint is not None and len(checkpoint) > 0 and not os.path.exists(checkpoint):
            raise ValueError(f"找不到checkpoint文件：{checkpoint}")

        if lora is not None and len(lora) > 0 and not os.path.exists(lora):
            raise ValueError(f"找不到lora文件：{lora}")

        if lora_alpha > 1.0 or lora_alpha < 0:
            raise ValueError("lora_alpha为0-1的小数")

        if ip_adapter_faceid_model and len(ip_adapter_faceid_model) > 0 and not os.path.exists(
                sd_info.ip_adapter_faceid_model_path + "/" + ip_adapter_faceid_model):
            raise ValueError(f"找不到ip_adapter_model文件：{ip_adapter_faceid_model}")

        log_handler.textViewer = self.get_log_viewer()
        aigc_config = config.get_aigc_config()
        images, seed = ip_adapter_faceid_pic(sd_origin_model_path=sd_info.main_model_path,
                                             ip_adapter_faceid_model_path=sd_info.ip_adapter_faceid_model_path + "/" + ip_adapter_faceid_model,
                                             insightface_model_path=sd_info.insightface_model_path,
                                             image_encoder_model_path=sd_info.image_encoder_model_path,
                                             input_image_path=input_img,
                                             prompt=prompt,
                                             negative_prompt=negative_prompt,
                                             checkpoint_path=checkpoint,
                                             lora_path=lora,
                                             num_images=img_num,
                                             guidance_scale=guidance_scale,
                                             seed=seed,
                                             num_inference_steps=num_inference_steps,
                                             lora_alpha=lora_alpha,
                                             height=img_height,
                                             width=img_width,
                                             log_step=aigc_config.get("log_step", 5),
                                             min_seed=aigc_config.get("min_seed", 1),
                                             max_seed=aigc_config.get("max_seed", 9999999999)
                                             )

        window.evaluate_js("vue.messageArrive('jllama提醒','图片生成成功','success')")

        result = {"seed": seed}
        images_base64 = []
        for image in images:
            # 转换为 Base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
            images_base64.append(img_str)
        result["images"] = images_base64
        return result

    def get_default_negative_prompt(self):
        return default_negative_prompt()