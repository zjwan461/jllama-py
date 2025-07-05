import json
import os.path

dic: dict = {}
user_dir = os.path.join(os.path.expanduser('~'))
if not os.path.exists(user_dir + "/jllama"):
    os.mkdir(user_dir + "/jllama")
config_path = os.path.join(user_dir, "jllama/config.json")


def get_default():
    return {
        "db_url": f"sqlite:///{user_dir}/jllama/db/jllama.db",
        "server": {
            "host": "127.0.0.1",
            "port": 5000
        },
        "model": "prd",
        "app_name": "jllama",
        "app_width": 1366,
        "app_height": 768,
        "llama_server_config_path": f"{user_dir}/jllama/llama_cpp_config.json",
        "ai_config": {
            "model_save_dir": f"{user_dir}/jllama/models",
            "llama_factory_port": 7860,
            "llama_factory_host": "0.0.0.0"
        },
        "proxy": {
            "http_proxy": "",
            "https_proxy": ""
        }
    }


def get_default_llama_server_config():
    return {
        "host": "0.0.0.0",
        "port": 8080,
        "models": [
            {
                "model": f"{user_dir}/models/Qwen/Qwen3-0.6B-GGUF/Qwen3-0.6B.gguf",
                "model_alias": "Qwen3-0.6B",
                "chat_format": None,
                "n_gpu_layers": -1,
                "offload_kqv": True,
                "n_threads": 12,
                "n_batch": 512,
                "n_ctx": 2048
            },
            {
                "model": f"{user_dir}/models/Qwen/Qwen3-1.7B-GGUF/Qwen3-1.7B.gguf",
                "model_alias": "Qwen3-1.7B",
                "n_gpu_layers": -1,
                "offload_kqv": True,
                "n_threads": 12,
                "n_batch": 512,
                "n_ctx": 2048
            }
        ]
    }


def read_config():
    global dic

    if not os.path.exists(config_path):
        dic = get_default()
        with open(config_path, "w") as f:
            f.write(json.dumps(dic, ensure_ascii=False, indent=4))
    else:
        with open(config_path, "r") as f:
            conf = f.read()
            dic = json.loads(conf)


read_config()


def get_llama_server_config_path():
    return dic.get("llama_server_config_path", f"{user_dir}/jllama/llama_cpp_config.json")


def get_value(key: str):
    return dic[key]


def get_app_name():
    return dic.get("app_name", "jllama")


def get_model():
    return dic.get("model", "prd")


def is_dev():
    return get_model() == "dev"


def is_prd():
    return get_model() == "prd"


def get_ai_config() -> dict:
    return dic.get("ai_config", {
        "model_save_dir": f"{user_dir}/jllama/models",
        "llama_factory_port": 7860,
        "llama_factory_host": "0.0.0.0"
    })


def get_app_height():
    return dic.get("app_height", 768)


def get_app_width():
    return dic.get("app_width", 1366)


def get_db_url():
    return dic.get("db_url", f"sqlite:///{user_dir}/jllama/db/jllama.db")


def get_server_config():
    return dic.get("server", {
        "host": "127.0.0.1",
        "port": 5000
    })


def save_ai_config(config: dict):
    dic["ai_config"] = config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)
    read_config()


def get_proxy_config() -> dict:
    return dic.get("proxy", {
        "http_proxy": "",
        "https_proxy": ""
    })


def save_proxy_config(config: dict):
    dic["proxy"] = config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)
    read_config()
