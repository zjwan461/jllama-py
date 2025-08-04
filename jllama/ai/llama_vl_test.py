from llama_cpp import Llama
from llama_cpp.llama_chat_format import Qwen25VLChatHandler

chat_handler = Qwen25VLChatHandler(clip_model_path=r"E:\models\unsloth\Qwen2___5-VL-7B-Instruct-GGUF\mmproj-BF16.gguf")
llm = Llama(
    model_path=r"E:\models\unsloth\Qwen2___5-VL-7B-Instruct-GGUF\Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf",
    chat_handler=chat_handler,
    n_ctx=2048,  # n_ctx should be increased to accommodate the image embedding
    n_gpu_layers=-1,
)
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "你是一个图像识别助手"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "描述图片？"},
                {"type": "image_url",
                 "image_url":
                     {
                         "url": "https://img-blog.csdnimg.cn/c8afaeb6d4064b63beae9836ce614f27.png"}
                 }
            ]
        }
    ]
)
print(response["choices"][0].get("message").get("content"))
