import socket
import platform

import GPUtil
import psutil
import wmi


def get_cpu_info():
    result = {}
    cores = psutil.cpu_count()
    result['cores'] = cores
    use_percent = psutil.cpu_percent(interval=1)
    result['use_percent'] = str(use_percent) + '%'
    result['free_percent'] = str(100 - use_percent) + '%'
    return result


def get_memory_info():
    result = {}
    # 获取系统内存信息
    memory = psutil.virtual_memory()

    # 总内存（以字节为单位）
    total_memory = memory.total
    # 已使用内存（以字节为单位）
    used_memory = memory.used
    # 内存使用率（百分比）
    memory_percent = memory.percent

    result['total_memory'] = f"{total_memory / (1024 * 1024 * 1024):.2f} GB"
    result['used_memory'] = f"{used_memory / (1024 * 1024 * 1024):.2f} GB"
    result['free_memory'] = f"{(total_memory - used_memory) / (1024 * 1024 * 1024):.2f} GB"
    result['memory_percent'] = f"{memory_percent}%"
    return result


def get_os_info():
    result = {'os': platform.system(), 'arch': platform.machine()}
    hostname = socket.gethostname()
    result['hostname'] = hostname
    result['ip'] = socket.gethostbyname(hostname)
    return result


def get_gpu_info():
    result = []
    gpus = GPUtil.getGPUs()
    if len(gpus) > 0:
        for gpu in gpus:
            item = {"name": f"{gpu.name}", "memory": f"{gpu.memoryTotal}", "driver": f"{gpu.driver}"}
            # 显存使用率
            result.append(item)
    else:
        try:
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                gpu_info = {
                    "name": gpu.Name,
                    "driver": gpu.DriverVersion,
                }
                memory = round(gpu.AdapterRAM / (1024 ** 3), 2) if gpu.AdapterRAM else "N/A"
                memory = "N/A" if memory < 0 else memory
                gpu_info["memory"] = memory
                result.append(gpu_info)

        except Exception as e:
            print(f"获取AMD GPU信息失败: {e}")
    return result

def is_cuda_available():
    gpus = GPUtil.getGPUs()
    return len(gpus) > 0

if __name__ == '__main__':
    res = get_cpu_info()
    print(res)
    res2 = get_memory_info()
    print(res2)
    res3 = get_os_info()
    print(res3)
    res4 = get_gpu_info()
    print(res4)
