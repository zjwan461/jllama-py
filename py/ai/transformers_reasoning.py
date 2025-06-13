import threading

from modelscope import snapshot_download


def download():
    snapshot_download("Qwen/Qwen3-0.6B", cache_dir="D:/models", allow_file_pattern="*")


# download()

model_name = "D:/models/Qwen/Qwen3-0.6B"


def reasoning():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    prompt = "Give me a short introduction to large language model."
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    # 推理矩阵
    print(generated_ids)
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print(response)


def reasoning_pipline():
    from transformers import pipeline, TextStreamer, TextIteratorStreamer
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    generator = pipeline(task="text-generation", model=model, tokenizer=tokenizer,
                         device_map="auto", torch_dtype="auto")
    prompt = "为什么天空是蓝色的"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    # streamer = TextStreamer(generator.tokenizer, skip_prompt=True, skip_special_tokens=True)
    # res = generator(messages, max_new_tokens=32768, streamer=streamer)
    streamer = TextIteratorStreamer(generator.tokenizer, skip_prompt=True, skip_special_tokens=True)

    t = threading.Thread(target=generator,
                         kwargs=dict(text_inputs=messages, max_new_tokens=32768, streamer=streamer, do_sample=True,
                                     temperature=0.8, top_k=40, top_p=0.95))
    t.start()

    generated_text = ""
    for new_text in streamer:
        print(new_text)
        generated_text += new_text

    print(generated_text)
    # print(json.dumps(res[0]["generated_text"], indent=4))


reasoning_pipline()
