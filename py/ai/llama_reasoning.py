import inspect
import json

from llama_cpp import Llama


class LlamaReasoning:

    def __init__(self, model_path, n_gpu_layers=-1, n_ctx=1024, temperature=0.8, top_k=30, top_p=0.9, n_threads=-1,
                 stream=False):
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.n_threads = n_threads
        self.stream = stream
        self.state = "stop"

    def init_model(self):
        self.llm = Llama(
            model_path=self.model_path,
            n_gpu_layers=self.n_gpu_layers,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
        )
        self.state = "init"

    def close_model(self):
        self.llm.close()

    def chat(self, messages):
        if self.state == "init":
            return self.chat_stream(messages) if self.stream else self.chat_blocking(messages)
        else:
            return "NOT_INITIALIZED"

    def chat_blocking(self, messages):
        output = self.llm.create_chat_completion(
            messages=messages,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            stream=False
        )
        return json.dumps(output)

    def chat_stream(self, messages):
        output = self.llm.create_chat_completion(
            messages=messages,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            stream=True
        )
        # print(json.dumps(output, indent=4))
        # print(output.get("choices")[0].get("message").get("content").get("message"))
        for line in output:
            yield json.dumps(line)
        else:
            yield "Done"


# print(json.dumps(output, indent=4))
# print(output.get("choices")[0].get("text"))

# for line in chat():
#     print(line, end=" ")

# chat()


if __name__ == '__main__':
    llm = LlamaReasoning("E:\models\Qwen\Qwen3-0.6B-GGUF\Qwen3-0.6B-Q8_0.gguf", stream=True)
    print("let`s chat!")
    while True:
        command = input("pls input command: ")
        if command == "init":
            llm.init_model()
            print("loaded model")
        elif command == "chat":
            while True:
                message = input("pls input message: ")
                if message == "quit":
                    break
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant.",
                    },
                    {"role": "user", "content": message},
                ]
                output = llm.chat(messages=messages)
                if inspect.isgenerator(output):
                    for token in output:
                        if token:
                            print(token)
                    else:
                        print()
                else:
                    print(output)
        elif command == "stop":
            llm.close_model()
            break
        else:
            print(f"no such command:{command}")
