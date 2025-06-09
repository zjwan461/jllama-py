import json
import py.util.systemInfo_util as sysInfoUtil

from py.util.logutil import Logger
from py.util.db_util import SqliteSqlalchemy, SysInfo

logger = Logger("Api.py")


class Api:

    def show_tips(self):
        return "today is a good day"

    def get_nav(self):
        f = open("py/nav.json", "r")
        conf = f.read()
        json_data = json.loads(conf)
        return json_data

    def get_sys_info(self):
        result = {"cpu": sysInfoUtil.get_cpu_info(), "memory": sysInfoUtil.get_memory_info(),
                  "gpus": sysInfoUtil.get_gpu_info(),
                  "os": sysInfoUtil.get_os_info(), "jllamaInfo": sysInfoUtil.get_jllama_info()}
        return result

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


if __name__ == '__main__':
    api = Api()
    api.show_tips()
