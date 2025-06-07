import json
import py.util.systemInfoUtil as sysInfoUtil

from py.util.logutil import Logger

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
                  "os": sysInfoUtil.get_os_info()}
        return result


if __name__ == '__main__':
    api = Api()
    api.show_tips()
