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
    tokens = tokenizer(texts, truncation=True, padding="max_length", max_length=512)
    tokens["labels"] = tokens["input_ids"].copy()
    # print(tokens)
    return tokens


tokenized_train_dataset = train_dataset.map(tokenizer_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(tokenizer_function, batched=True)
print(tokenized_train_dataset[0])

from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,

)

model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, device_map="auto")
print("已量化")

from peft import get_peft_model, LoraConfig, TaskType
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print("已添加Lora")

from transformers import TrainingArguments, Trainer
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=3e-5,
    num_train_epochs=10,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    eval_strategy="steps",
    eval_steps=10,
    logging_dir="./logs",
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
