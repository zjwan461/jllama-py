# model_path = "/data/download/models/Qwen/Qwen2.5-VL-7B-Instruct"
model_path = "/data/download/models/Qwen/Qwen2.5-VL-3B-Instruct-AWQ"

from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor, TextStreamer, \
    TextIteratorStreamer

from qwen_vl_utils import process_vision_info

import threading

import torch

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    model_path, torch_dtype="auto", device_map="auto"
)

processor = AutoProcessor.from_pretrained(model_path)

# The default range for the number of visual tokens per image in the model is 4-16384.
# You can set min_pixels and max_pixels according to your needs, such as a token range of 256-1280, to balance performance and cost.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://img-blog.csdnimg.cn/c8afaeb6d4064b63beae9836ce614f27.png",
            },
            {
                "type": "image",
                "image": "file:///home/formssi/develop/train/generate_0.png",
            },
            {"type": "text", "text": "描述图片"},
        ],
    }
]

# Preparation for inference
text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to(model.device)

# Inference: Generation of the output
# generated_ids = model.generate(**inputs, max_new_tokens=128)
# generated_ids_trimmed = [
#     out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
# ]
# output_text = processor.batch_decode(
#     generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
# )
# print(output_text)

# streamer = TextStreamer(processor,skip_prompt=True,skip_special_tokens=True)
# model.generate(**inputs, max_new_tokens=2048, streamer=streamer)


streamer = TextIteratorStreamer(processor, skip_prompt=True, skip_special_tokens=True)

t = threading.Thread(target=model.generate, kwargs=dict(inputs, streamer=streamer, max_new_tokens=2048, do_sample=True))
t.start()

for token in streamer:
    print(token, end="")
t.join()
