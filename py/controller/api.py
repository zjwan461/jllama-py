import json

import py.util.systemInfo_util as sysInfoUtil

from py.util.logutil import Logger
from py.util.db_util import SqliteSqlalchemy, SysInfo, Model
import py.config as config
import orjson
import py.util.model_file_util as model_file_util

logger = Logger("Api.py")


class Api:

    def show_tips(self):
        return "today is a good day"

    def get_nav(self):
        f = open("py/nav.json", "r", encoding="utf-8")
        conf = f.read()
        json_data = json.loads(conf)
        return json_data

    def get_sys_info(self):
        result = {"cpu": sysInfoUtil.get_cpu_info(), "memory": sysInfoUtil.get_memory_info(),
                  "gpus": sysInfoUtil.get_gpu_info(),
                  "os": sysInfoUtil.get_os_info(), "jllamaInfo": sysInfoUtil.get_jllama_info()}
        return orjson.dumps(result).decode("utf-8")

    def init_env(self):
        session = SqliteSqlalchemy().session
        result = session.query(SysInfo).all()
        if len(result) <= 0:
            try:
                os_info = sysInfoUtil.get_os_info()
                gpu_platform = "cuda" if sysInfoUtil.is_cuda_available() else "cpu"
                sys_info = SysInfo(id=999, os_arch=os_info['arch'], platform=os_info['os'], gpu_platform=gpu_platform,
                                   cpp_version="0.3.9", factory_version="v0.9.2", self_version="v1.0")
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
                    r_list.append(item.to_dic())
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
        model = Model(name=params.get('name'), repo=params.get('repo'),
                      download_platform=params.get('download_platform'),
                      save_dir=config.get_ai_config().get_model_save_dir(),
                      import_dir=config.get_ai_config().get_model_import_dir())

        session = SqliteSqlalchemy().session
        try:
            old = session.query(Model).filter(Model.name == model.name).first()
            if old:
                old.name = model.name
                old.repo = model.repo
                old.download_platform = model.download_platform
                old.save_dir = model.save_dir
                old.import_dir = model.import_dir
            else:
                session.add(model)
            session.commit()
            return "success"
        except Exception as e:
            logger.error(e)
            session.rollback()
            return "error"
        finally:
            session.close()

    def search_model_file(self, params):
        return model_file_util.get_model_file(repo=params.get("repo"), revision=params.get("revision"),
                                              root=params.get("root"))

    def delete_model(self, id):
        session = SqliteSqlalchemy().session
        try:
            record = session.query(Model).get(id)
            if record:
                session.delete(record)
                session.commit()
            else:
                logger.info(f"can not found model with id={id}")
        except Exception as e:
            logger.error(e)
            session.rollback()
        finally:
            session.close()


if __name__ == '__main__':
    api = Api()
    api.show_tips()
