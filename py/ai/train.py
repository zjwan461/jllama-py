from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = r"E:\models\Qwen\Qwen3-0.6B"
#
model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda")

tokenizer = AutoTokenizer.from_pretrained(model_path)

print("-----------模型加载成功--------------")

# 准备数据集
from datasets import load_dataset, load_from_disk

# dataset = load_from_disk(r"E:\datasets\Brain_teasers")
# print(dataset)
dataset = load_dataset("json", data_files={"train": r"E:\datasets\Brain_teasers\data.json"}, split="train")
print(dataset)

train_test_split = dataset.train_test_split(test_size=0.1)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]
print(f"训练集的样本数：{len(train_dataset)}")
print(f"验证集的样本数：{len(eval_dataset)}")


def tokenizer_function(samples):
    texts = [f"{instruction}\n{output}" for instruction, output in zip(samples["instruction"], samples["output"])]
    # print(texts)
    # max_length输入序列分词后的最大长度。==截断长度cutoff_len
    tokens = tokenizer(texts, truncation=True, padding="max_length", max_length=2048)
    tokens["labels"] = tokens["input_ids"].copy() # 自回归模型的labels=input_ids,但是比input_ids慢一位(通过t-1个token预测第t个token)
    # print(tokens)
    return tokens


tokenized_train_dataset = train_dataset.map(tokenizer_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(tokenizer_function, batched=True)
# print(tokenized_train_dataset[0])

from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
)

model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, device_map="auto")
print("已量化")

from peft import get_peft_model, LoraConfig, TaskType, PeftModel
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    # target_modules=["q_proj", "v_proj"],
    target_modules="all",
    lora_dropout=0.00
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print("已添加Lora")

from transformers import TrainingArguments, Trainer
training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    learning_rate=5e-5,# 学习率
    num_train_epochs=10,#轮次,训练多少轮
    per_device_train_batch_size=4,#每个 GPU 处理的样本数量。
    gradient_accumulation_steps=8,#梯度累积的步数。将一个大批次（batch）分成 gradient_accumulation_steps 个小批次（micro-batches）。
                                  #每个小批次计算梯度后，不立即更新参数，而是累积这些梯度。
                                  #当累积的梯度数量达到 gradient_accumulation_steps 时，才用累积的总梯度更新一次模型参数。
    bf16=True,  #计算类型，使用bfloat16混合精度
    logging_steps=5,
    warmup_steps=0,
    save_steps=100,
    eval_strategy="steps",
    eval_steps=10,
    logging_dir="./logs",
    max_grad_norm=1.0,  #用于梯度裁剪的范数
    lr_scheduler_type="cosine", #学习率调度器
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_eval_dataset,
)
print("开始训练")
trainer.train()
print("训练完成")

print("开始保存lora")
model.save_pretrained("./lora")
tokenizer.save_pretrained("./lora")
print("保存lora结束")

print("开始合并lora到原始模型")
origin_model = AutoModelForCausalLM.from_pretrained(model_path)
model = PeftModel.from_pretrained(origin_model, "./lora")
model = model.merge_and_unload()
model.save_pretrained("./final")
tokenizer.save_pretrained("./final")
print("合并结束")



