import json

from llama_cpp import Llama

llm = Llama(
    model_path="E:\models\Qwen\Qwen3-1___7B-GGUF\Qwen3-1.7B-Q8_0.gguf",
    # n_gpu_layers=-1, # Uncomment to use GPU acceleration
    # seed=1337, # Uncomment to set a specific seed
    n_ctx=2048,  # Uncomment to increase the context window
    # chat_format="qwen"
)



def chat():
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": "为什么天是蓝色的？"},
        ],
        temperature=0.8,
        top_k=40,
        top_p=0.95,
        stream=True
    )
    # print(json.dumps(output, indent=4))
    # print(output.get("choices")[0].get("message").get("content").get("message"))
    for line in output:
        yield line.get("choices")[0].get("delta").get("content")
# print(json.dumps(output, indent=4))
# print(output.get("choices")[0].get("text"))

for line in chat():
    print(line)

# chat()