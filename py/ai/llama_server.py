from __future__ import annotations

import os
import sys
import argparse
import threading

import uvicorn

from llama_cpp.server.app import create_app
from llama_cpp.server.settings import (
    Settings,
    ServerSettings,
    ModelSettings,
    ConfigFileSettings,
)
from llama_cpp.server.cli import add_args_from_model, parse_model_from_args

"""Example FastAPI server for llama.cpp.

To run this example:

```bash
pip install fastapi uvicorn sse-starlette pydantic-settings
export MODEL=../models/7B/...
```

Then run:
```
uvicorn llama_cpp.server.app:create_app --reload
```

or

```
python3 -m llama_cpp.server
```

Then visit http://localhost:8000/docs to see the interactive API docs.

"""

state = "stop"
server_port: int


def run_llama_server_async(model: str, model_alias=None, n_gpu_layers=None,
                           split_mode=None, main_gpu=None, tensor_split=None, vocab_only=None, use_mmap=None,
                           use_mlock=None, kv_overrides=None, rpc_servers=None, seed=None, n_ctx=None, n_batch=None,
                           n_ubatch=None, n_threads=None, n_threads_batch=None, rope_scaling_type=None,
                           rope_freq_base=None, rope_freq_scale=None, yarn_ext_factor=None, yarn_attn_factor=None,
                           yarn_beta_fast=None, yarn_beta_slow=None, yarn_orig_ctx=None, mul_mat_q=None,
                           logits_all=None, embedding=None, offload_kqv=None, flash_attn=None,
                           last_n_tokens_size=None, lora_base=None, lora_path=None, numa=None, chat_format=None,
                           clip_model_path=None, cache=None, cache_type=None, cache_size=None,
                           hf_tokenizer_config_path=None, hf_pretrained_model_name_or_path=None,
                           hf_model_repo_id=None, draft_model=None, draft_model_num_pred_tokens=None, type_k=None,
                           type_v=None, verbose=None, host=None, port=None, ssl_keyfile=None, ssl_certfile=None,
                           api_key=None, interrupt_requests=None, disable_ping_events=None, root_path=None,
                           config_file=None):

    server_thread = threading.Thread(target=run_llama_server, args=(model, model_alias, n_gpu_layers,
                                                                    split_mode, main_gpu, tensor_split, vocab_only,
                                                                    use_mmap,
                                                                    use_mlock, kv_overrides, rpc_servers, seed, n_ctx,
                                                                    n_batch,
                                                                    n_ubatch, n_threads, n_threads_batch,
                                                                    rope_scaling_type,
                                                                    rope_freq_base, rope_freq_scale, yarn_ext_factor,
                                                                    yarn_attn_factor,
                                                                    yarn_beta_fast, yarn_beta_slow, yarn_orig_ctx,
                                                                    mul_mat_q,
                                                                    logits_all, embedding, offload_kqv, flash_attn,
                                                                    last_n_tokens_size, lora_base, lora_path, numa,
                                                                    chat_format,
                                                                    clip_model_path, cache, cache_type, cache_size,
                                                                    hf_tokenizer_config_path,
                                                                    hf_pretrained_model_name_or_path,
                                                                    hf_model_repo_id, draft_model,
                                                                    draft_model_num_pred_tokens, type_k,
                                                                    type_v, verbose, host, port, ssl_keyfile,
                                                                    ssl_certfile,
                                                                    api_key, interrupt_requests, disable_ping_events,
                                                                    root_path,
                                                                    config_file))

    server_thread.start()
    return server_thread


def run_llama_server(model: str, model_alias=None, n_gpu_layers=None,
                     split_mode=None, main_gpu=None, tensor_split=None, vocab_only=None, use_mmap=None,
                     use_mlock=None, kv_overrides=None, rpc_servers=None, seed=None, n_ctx=None, n_batch=None,
                     n_ubatch=None, n_threads=None, n_threads_batch=None, rope_scaling_type=None,
                     rope_freq_base=None, rope_freq_scale=None, yarn_ext_factor=None, yarn_attn_factor=None,
                     yarn_beta_fast=None, yarn_beta_slow=None, yarn_orig_ctx=None, mul_mat_q=None,
                     logits_all=None, embedding=None, offload_kqv=None, flash_attn=None,
                     last_n_tokens_size=None, lora_base=None, lora_path=None, numa=None, chat_format=None,
                     clip_model_path=None, cache=None, cache_type=None, cache_size=None,
                     hf_tokenizer_config_path=None, hf_pretrained_model_name_or_path=None,
                     hf_model_repo_id=None, draft_model=None, draft_model_num_pred_tokens=None, type_k=None,
                     type_v=None, verbose=None, host=None, port=None, ssl_keyfile=None, ssl_certfile=None,
                     api_key=None, interrupt_requests=None, disable_ping_events=None, root_path=None,
                     config_file=None):
    global state
    global server_port
    server_port = port if port is not None else 8000

    description = "🦙 Llama.cpp python server. Host your own LLMs!🚀"
    parser = argparse.ArgumentParser(description=description)

    add_args_from_model(parser, Settings)
    parser.add_argument(
        "--config_file",
        type=str,
        help="Path to a config file to load.",
    )
    server_settings: ServerSettings | None = None
    model_settings: list[ModelSettings] = []
    # args = parser.parse_args()
    args = argparse.Namespace(model=model, model_alias=model_alias, n_gpu_layers=n_gpu_layers,
                              split_mode=split_mode, main_gpu=main_gpu, tensor_split=tensor_split,
                              vocab_only=vocab_only, use_mmap=use_mmap,
                              use_mlock=use_mlock, kv_overrides=kv_overrides, rpc_servers=rpc_servers, seed=seed,
                              n_ctx=n_ctx, n_batch=n_batch,
                              n_ubatch=n_ubatch, n_threads=n_threads, n_threads_batch=n_threads_batch,
                              rope_scaling_type=rope_scaling_type,
                              rope_freq_base=rope_freq_base, rope_freq_scale=rope_freq_scale,
                              yarn_ext_factor=yarn_ext_factor, yarn_attn_factor=yarn_attn_factor,
                              yarn_beta_fast=yarn_beta_fast, yarn_beta_slow=yarn_beta_slow, yarn_orig_ctx=yarn_orig_ctx,
                              mul_mat_q=mul_mat_q,
                              logits_all=logits_all, embedding=embedding, offload_kqv=offload_kqv,
                              flash_attn=flash_attn,
                              last_n_tokens_size=last_n_tokens_size, lora_base=lora_base, lora_path=lora_path,
                              numa=numa, chat_format=chat_format,
                              clip_model_path=clip_model_path, cache=cache, cache_type=cache_type,
                              cache_size=cache_size,
                              hf_tokenizer_config_path=hf_tokenizer_config_path,
                              hf_pretrained_model_name_or_path=hf_pretrained_model_name_or_path,
                              hf_model_repo_id=hf_model_repo_id, draft_model=draft_model,
                              draft_model_num_pred_tokens=draft_model_num_pred_tokens, type_k=type_k,
                              type_v=type_v, verbose=verbose, host=host, port=port, ssl_keyfile=ssl_keyfile,
                              ssl_certfile=ssl_certfile,
                              api_key=api_key, interrupt_requests=interrupt_requests,
                              disable_ping_events=disable_ping_events, root_path=root_path,
                              config_file=config_file)

    try:
        # Load server settings from config_file if provided
        config_file = os.environ.get("CONFIG_FILE", args.config_file)
        if config_file:
            if not os.path.exists(config_file):
                raise ValueError(f"Config file {config_file} not found!")
            with open(config_file, "rb") as f:
                # Check if yaml file
                if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                    import yaml
                    import json

                    config_file_settings = ConfigFileSettings.model_validate_json(
                        json.dumps(yaml.safe_load(f))
                    )
                else:
                    config_file_settings = ConfigFileSettings.model_validate_json(
                        f.read()
                    )
                server_settings = ServerSettings.model_validate(config_file_settings)
                model_settings = config_file_settings.models
        else:
            server_settings = parse_model_from_args(ServerSettings, args)
            model_settings = [parse_model_from_args(ModelSettings, args)]
    except Exception as e:
        print(e, file=sys.stderr)
        parser.print_help()
        sys.exit(1)  # todo 修改
    assert server_settings is not None
    assert model_settings is not None
    app = create_app(
        server_settings=server_settings,
        model_settings=model_settings,
    )
    state = "running"
    uvicorn.run(
        app,
        host=os.getenv("HOST", server_settings.host),
        port=int(os.getenv("PORT", server_settings.port)),
        ssl_keyfile=server_settings.ssl_keyfile,
        ssl_certfile=server_settings.ssl_certfile,
    )


if __name__ == "__main__":
    run_llama_server(model="E:\models\Qwen\Qwen3-0.6B.gguf", config_file="../llama_cpp_config.json")
