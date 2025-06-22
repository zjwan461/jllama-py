import os.path

from py.ai.llama_reasoning import LlamaReasoning
from py.ai.transformers_reasoning import TransformersReasoning
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
        llama_cpp_reasoning = LlamaReasoning(model_path=file_download.file_path, n_gpu_layers=kwargs["ngl"],
                                             n_ctx=kwargs["ctxSize"],
                                             temperature=kwargs["temperature"], top_k=kwargs["top_k"],
                                             top_p=kwargs["top_p"],
                                             n_threads=kwargs["threads"], stream=kwargs["stream"])
        llama_cpp_reasoning.init_model()
        running_llama[model_id] = llama_cpp_reasoning
    elif model.type == "hf":
        file_path = model.save_dir
        if not os.path.exists(file_path):
            raise Exception(f"can not found model file path: {file_path}")
        transformers_reasoning = TransformersReasoning(model_name=file_path, torch_dtype=kwargs["torch_dtype"],
                                                       max_new_tokens=kwargs["ctxSize"],
                                                       stream=kwargs["stream"], temperature=kwargs["temperature"],
                                                       top_k=kwargs["top_k"],
                                                       top_p=kwargs["top_p"])
        transformers_reasoning.init_model()
        running_transformers[model_id] = transformers_reasoning
    else:
        raise Exception(f"model type: {model.type} is not supported")

def stop_reasoning(model_id):
    global running_llama
    global running_transformers
    if model_id in running_llama:
        llama_cpp_reasoning = running_llama[model_id]
        llama_cpp_reasoning.close_model()
        del running_llama[model_id]
    elif model_id in running_transformers:
        running_transformers_reasoning = running_transformers[model_id]
        running_transformers_reasoning.close_model()
        del running_transformers[model_id]


def stop_all_reasoning():
    global running_llama
    global running_transformers
    for model_id in running_llama:
        llama_cpp_reasoning = running_llama[model_id]
        llama_cpp_reasoning.close_model()
        del running_llama[model_id]

    for model_id in running_transformers:
        running_transformers_reasoning = running_transformers[model_id]
        running_transformers_reasoning.close_model()
        del running_transformers[model_id]
