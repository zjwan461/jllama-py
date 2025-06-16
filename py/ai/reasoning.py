import os.path

from py.ai.llama_reasoning import LlamaReasoning
from py.util.db_util import Model, FileDownload

running_llama = {}
running_transformers = {}


def run_reasoning(model: Model, file_download: FileDownload = None, **kwargs):
    global running_llama
    global running_transformers
    model_id = model.id
    if model_id in running_llama or model_id in running_transformers:
        raise Exception(f"Model: {model.name} is running")

    if model.type == "gguf":
        if file_download is None:
            raise Exception("gguf model must provide a gguf file")
        llama_cpp_reasoning = LlamaReasoning(model_path=file_download.file_path, n_gpu_layers=kwargs["ngl"], n_ctx=kwargs["ctxSize"],
                                             temperature=kwargs["temperature"], top_k=kwargs["top_k"],
                                             top_p=kwargs["top_p"],
                                             n_threads=kwargs["threads"], stream=kwargs["stream"])
        llama_cpp_reasoning.init_model()
        running_llama[model_id] = llama_cpp_reasoning
    else:
        file_path = os.path.join(model.save_dir, model.repo)
        if not os.path.exists(file_path):
            raise Exception(f"can not found model file path: {file_path}")

        # todo transformers model reasoning
        raise Exception("Not support yet")

def stop_reasoning(model_id):
    global running_llama
    global running_transformers
    if model_id in running_llama:
        llama_cpp_reasoning = running_llama[model_id]
        llama_cpp_reasoning.close_model()
        del running_llama[model_id]
    elif model_id in running_transformers:
        # todo transformers model stop reasoning
        del running_transformers[model_id]

