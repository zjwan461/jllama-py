import json
import threading
import time
import uuid

import torch
from transformers import pipeline, TextStreamer, TextIteratorStreamer
from transformers import AutoModelForCausalLM, AutoTokenizer
from jllama.ai.base_reasoning import BaseReasoning


# model_name = "E:\models\Qwen\Qwen3-4B"


# def reasoning():
#     model = AutoModelForCausalLM.from_pretrained(
#         model_name,
#         torch_dtype="auto",
#         device_map="auto"
#     )
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#
#     prompt = "Give me a short introduction to large language model."
#     messages = [
#         {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
#         {"role": "user", "content": prompt}
#     ]
#     text = tokenizer.apply_chat_template(
#         messages,
#         tokenize=False,
#         add_generation_prompt=True,
#         enable_thinking=True
#     )
#     model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
#
#     generated_ids = model.generate(
#         **model_inputs,
#         max_new_tokens=512
#     )
#     generated_ids = [
#         output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
#     ]
#
#     # 推理矩阵
#     print(generated_ids)
#     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#
#     print(response)


# def reasoning_pipline():
#     model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     generator = pipeline(task="text-generation", model=model, tokenizer=tokenizer,
#                          device_map="auto", torch_dtype="auto")
#     prompt = "为什么天空是蓝色的?还有把大象放进冰箱需要几步？"
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": prompt}
#     ]
#
#     streamer = TextIteratorStreamer(generator.tokenizer, skip_prompt=True, skip_special_tokens=True)
#
#     t = threading.Thread(target=generator,
#                          kwargs=dict(text_inputs=messages, streamer=streamer, do_sample=True,
#                                      temperature=0.8, top_k=40, top_p=0.9, max_new_tokens=2048))
#     t.start()
#
#     for new_text in streamer:
#         yield new_text
#     else:
#         yield "Done"
#
#     t.join()


# for token in reasoning_pipline():
#     print(token, end="")


class TransformersReasoning(BaseReasoning):
    def __init__(self, model_name: str, torch_dtype: str or torch.dtype, max_new_tokens: int, stream: bool = False,
                 temperature=0.8,
                 top_k=40, top_p=0.9):
        self.stream = stream
        self.max_new_tokens = int(max_new_tokens)
        self.temperature = float(temperature)
        self.top_k = int(top_k)
        self.top_p = float(top_p)
        self.model_name = model_name
        self.torch_dtype = torch_dtype

    def init_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=self.torch_dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.generator = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer,
                                  device_map="auto", torch_dtype="auto")

    def chat_blocking(self, messages):
        response = self.generator(text_inputs=messages, do_sample=True,
                                  temperature=self.temperature, top_k=self.top_k, top_p=self.top_p,
                                  max_new_tokens=self.max_new_tokens)
        id = str(uuid.uuid4())
        content = response[0]["generated_text"][-1]
        result = {"id": id, "model": self.model_name, "created": int(time.time()), "object": "chat.completion",
                  "choices": [{"index": 0, "message": content, "logprobs": None, "finish_reason": "stop"}]}
        return json.dumps(result)

    def chat_stream(self, messages):
        streamer = TextIteratorStreamer(self.generator.tokenizer, skip_prompt=True, skip_special_tokens=True)
        t = threading.Thread(target=self.generator,
                             kwargs=dict(text_inputs=messages, streamer=streamer, do_sample=True,
                                         temperature=self.temperature, top_k=self.top_k, top_p=self.top_p,
                                         max_new_tokens=self.max_new_tokens))
        t.start()

        id = str(uuid.uuid4())
        for new_text in streamer:
            token = {"id": id, "model": self.model_name, "created": int(time.time()), "object": "chat.completion.chunk",
                     "choices": [{"index": 0, "delta": {"content": new_text, "role": "assistant"}, "logprobs": None,
                                  "finish_reason": None}]}
            yield f"data: {json.dumps(token)}\n\n"
        else:
            token = {"id": id, "model": self.model_name, "created": int(time.time()), "object": "chat.completion.chunk",
                     "choices": [{"index": 0, "delta": {"content": "", "role": "assistant"}, "logprobs": None,
                                  "finish_reason": "stop"}]
                     }
            yield f"data: {json.dumps(token)}"

        t.join()

    def close_model(self):
        # 使用完模型后，卸载并释放 GPU 内存
        del self.model  # 删除模型变量
        del self.tokenizer
        del self.generator
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # 清空 CUDA 缓存


if __name__ == '__main__':
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": "什么东西越生气，它就越大？"}
    ]
    reasoning = TransformersReasoning(r"F:\workspaces\jllama-jllama\final", torch.bfloat16, 2024, temperature=0.6)
    reasoning.init_model()
    response = reasoning.chat_blocking(messages=messages)
    print(response)

    # for chunk in reasoning.chat_stream(messages=messages):
    #     print(chunk)

    reasoning.close_model()
