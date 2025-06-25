import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = r"E:\models\Qwen\Qwen3-0.6B"
# 加载原始模型。如果需要使用bnb量化策略可忽略，在加载bnb量化模型时再进行模型加载，只需要加载tokenizer。
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16).to(  # 使用bf16加载原始模型，降低显存占用
    "cuda", use_flash_attention_2=True)
# 启用梯度检查点，节省激活值显存
model.gradient_checkpointing_enable()
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("-----------模型加载成功--------------")

# 准备数据集
from datasets import load_dataset, load_from_disk

dataset = load_dataset("json", data_files={"train": r"E:\datasets\Brain_teasers\data.json"}, split="train")
print(dataset)

# 设置数据集和测试集的比例，如果不需要测试集剋跳过这一步
train_test_split = dataset.train_test_split(test_size=0.1)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]
print(f"训练集的样本数：{len(train_dataset)}")
print(f"验证集的样本数：{len(eval_dataset)}")


def tokenizer_function(samples):
    texts = [f"{instruction}\n{input}\n{output}" for instruction, input, output in
             zip(samples["instruction"], samples["input"], samples["output"])]
    # print(texts)
    # max_length输入序列分词后的最大长度。==截断长度cutoff_len
    tokens = tokenizer(texts, truncation=True, padding="longest", max_length=512)  # 使用批次中数据集的最大长度进行填充--显著减少显存占用
    tokens["labels"] = tokens["input_ids"].copy()  # 自回归模型的labels=input_ids,但是比input_ids慢一位(通过t-1个token预测第t个token)
    # print(tokens)
    return tokens


# 将数据集分词，如果数据集不包含测试集，可将整个数据集分词为训练集分词。否则需要将训练集和测试集分别分词
tokenized_train_dataset = train_dataset.map(tokenizer_function, batched=True)
# tokenized_train_dataset = dataset.map(tokenizer_function, batched=True)
tokenized_eval_dataset = eval_dataset.map(tokenizer_function, batched=True)
# print(tokenized_train_dataset[0])

# 开启bnb量化，理论上可降低显存占用
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, device_map="auto")
print("已量化")

from peft import get_peft_model, LoraConfig, TaskType, PeftModel
import torch.nn as nn


# 动态获取模型中的所有线性层
def get_all_linear_layers(model):
    target_modules = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            # 提取模块名称（不含父级路径）
            module_name = name.split(".")[-1]
            if module_name not in target_modules:
                target_modules.append(module_name)
    return target_modules


target_modules = get_all_linear_layers(model)

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    # target_modules=["q_proj", "v_proj"],
    target_modules=target_modules,
    lora_dropout=0.05
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print("已添加Lora")

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    learning_rate=5e-5,  # 学习率
    num_train_epochs=10,  # 轮次,训练多少轮
    per_device_train_batch_size=2,  # 每个 GPU 处理的样本数量。
    gradient_accumulation_steps=8,  # 梯度累积的步数。将一个大批次（batch）分成 gradient_accumulation_steps 个小批次（micro-batches）。
    # 每个小批次计算梯度后，不立即更新参数，而是累积这些梯度。
    # 当累积的梯度数量达到 gradient_accumulation_steps 时，才用累积的总梯度更新一次模型参数。
    bf16=True,  # 计算类型，使用bfloat16混合精度
    logging_steps=5,
    warmup_steps=0,
    save_steps=100,
    eval_strategy="no",  # step or epoch or no
    eval_steps=10,
    logging_dir="./logs",
    max_grad_norm=1.0,  # 用于梯度裁剪的范数
    lr_scheduler_type="linear",  # 学习率调度器
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    # eval_dataset=tokenized_eval_dataset,
)
print("开始训练")
trainer.train()
print("训练完成")

print("开始保存lora")
model.save_pretrained("./lora")
tokenizer.save_pretrained("./lora")
print("保存lora结束")

print("开始合并lora到原始模型")
model = AutoModelForCausalLM.from_pretrained(model_path)
model = PeftModel.from_pretrained(model, "./lora")
model = model.merge_and_unload()
model.save_pretrained("./final")
tokenizer.save_pretrained("./final")
print("合并结束")
