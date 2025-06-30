# 模型微调
import gc
import os.path
import shutil
import time

import torch
from datasets import load_dataset
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM, TrainingArguments, Trainer, \
    TrainerCallback, TrainerState, TrainerControl
from peft import get_peft_model, LoraConfig, TaskType, PeftModel
import torch.nn as nn
from py.util.logutil import Logger

logger = Logger("model_finetuning")


class SimpleTrainerCallback(TrainerCallback):

    def __init__(self):
        # 训练状态，初始为false表示未开始训练
        self.train_state = False

    def on_train_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        # 标记开始训练
        self.train_state = True
        pass

    def on_epoch_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        pass

    def on_epoch_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        pass

    def on_step_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        if not self.train_state:
            control.should_training_stop = True

    def on_step_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        pass

    def on_log(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        max_steps = state.max_steps
        history = state.log_history[-1]
        step = history["step"]
        logger.info(f"训练进度: {step}/{max_steps} {history}")


# 模型对象
model = None
# 分词器对象
tokenizer = None
# 训练器callback
train_callback = SimpleTrainerCallback()
# 训练器
trainer = None


def train(model_path: str, torch_dtype: str or torch.dtype, dataset_path: str, train_output_dir: str,
          lora_save_dir: str, fin_tuning_merge_dir: str,
          dataset_test_size: float = 0.0, dataset_padding: str = "longest", dataset_max_length: int = 512,
          bnb_4bit: bool = False, bnb_8bit: bool = False, lora_r: int = 8, lora_alpha: int = 16,
          lora_target: str or list = "all", lora_dropout: float = 0.0, learning_rate: float = 5e-5,
          num_train_epochs: int = 3, per_device_train_batch_size: int = 2, gradient_accumulation_steps: int = 8,
          bf16: bool = True, fp16: bool = False, max_grad_norm: float = 1.0, lr_scheduler_type: str = "cosine",
          logging_steps: int = 5, warmup_steps: int = 0, save_steps: int = 100, eval_steps: int = 10,
          save_strategy: str = "steps", offload_folder: str = "./tmp"):
    global model, tokenizer, train_callback, trainer
    # 1. tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    logger.info("已加载分词器")
    dataset = load_dataset("json", data_files={"train": dataset_path}, split="train")

    train_dataset = dataset
    tokenized_eval_dataset = None
    eval_strategy = "no"
    if dataset_test_size > 0.0:
        train_test_split = dataset.train_test_split(dataset_test_size)
        train_dataset = train_test_split["train"]
        eval_dataset = train_test_split["test"]
        logger.info(f"获取验证集的样本数：{len(eval_dataset)}")
        tokenized_eval_dataset = eval_dataset.map(tokenizer_function,
                                                  fn_kwargs={"tokenizer": tokenizer, "dataset_padding": dataset_padding,
                                                             "dataset_max_length": dataset_max_length}, batched=True)
        eval_strategy = "epoch"
    logger.info(f"获取训练集的样本数：{len(train_dataset)}")

    tokenized_train_dataset = train_dataset.map(tokenizer_function,
                                                fn_kwargs={"tokenizer": tokenizer, "dataset_padding": dataset_padding,
                                                           "dataset_max_length": dataset_max_length}, batched=True)
    bnb_config = None
    if bnb_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
        )
    elif bnb_8bit:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
    logger.info("开始加载模型")
    model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config,
                                                 device_map="auto", torch_dtype=torch_dtype,
                                                 # attn_implementation="flash_attention_2" # 能加速推理，需要安装flash_attn, 也可以考虑unsloth
                                                 )

    # 启用梯度检查点，节省激活值显存
    # model.gradient_checkpointing_enable()
    logger.info("成功加载模型")

    if lora_target == 'all':
        target_modules = get_all_linear_layers(model)
        logger.info(f"成功获取所有线性层{target_modules}")
    else:
        target_modules = lora_target
        logger.info(f"成功获取目标层{target_modules}")

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_r,
        lora_alpha=lora_alpha,
        # target_modules=["q_proj", "v_proj"],
        target_modules=target_modules,
        lora_dropout=lora_dropout
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    logger.info("成功加载lora模型")

    training_args = TrainingArguments(
        output_dir=train_output_dir,
        overwrite_output_dir=True,
        learning_rate=learning_rate,  # 学习率
        num_train_epochs=num_train_epochs,  # 轮次,训练多少轮
        per_device_train_batch_size=per_device_train_batch_size,  # 每个 GPU 处理的样本数量。
        gradient_accumulation_steps=gradient_accumulation_steps,
        # 梯度累积的步数。将一个大批次（batch）分成 gradient_accumulation_steps 个小批次（micro-batches）。
        # 每个小批次计算梯度后，不立即更新参数，而是累积这些梯度。
        # 当累积的梯度数量达到 gradient_accumulation_steps 时，才用累积的总梯度更新一次模型参数。
        bf16=bf16,  # 计算类型，使用bfloat16混合精度
        fp16=fp16,
        logging_steps=logging_steps,
        warmup_steps=warmup_steps,
        save_strategy=save_strategy,
        save_steps=save_steps,
        eval_strategy=eval_strategy,  # steps or epoch or no
        eval_steps=eval_steps,
        logging_dir="./logs",
        max_grad_norm=max_grad_norm,  # 用于梯度裁剪的范数
        lr_scheduler_type=lr_scheduler_type,  # 学习率调度器
        label_names=["labels"],  # 指定label名称
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_eval_dataset,
        callbacks=[train_callback]
    )

    train_start = time.time()
    logger.info("开始训练")
    trainer.train()
    train_end = time.time()
    train_use = train_end - train_start
    logger.info(f"训练完成,用时{train_use}s")

    merge_use = None
    break_train = False
    # 如果此时train_state is true，则保存lora模型
    if is_training():
        logger.info(f"开始保存lora到{lora_save_dir}")
        model.save_pretrained(lora_save_dir)
        tokenizer.save_pretrained(lora_save_dir)
        logger.info("保存lora结束")

        merge_start = time.time()
        logger.info(f"开始合并lora到原始模型{fin_tuning_merge_dir}")
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        model = PeftModel.from_pretrained(model,  # 原始模型目录
                                          lora_save_dir,  # lora保存目录
                                          offload_folder=offload_folder,
                                          # 模型临时卸载磁盘的目录，在显存和内存都占满的情况下会卸载模型到磁盘做临时缓存，可以在训练后删除
                                          # Create empty adapter weights on meta device before loading the saved weights. Useful to speed up the process.-简言之可以加速
                                          low_cpu_mem_usage=True,
                                          )
        model = model.merge_and_unload()
        model.save_pretrained(fin_tuning_merge_dir)
        tokenizer.save_pretrained(fin_tuning_merge_dir)
        merge_end = time.time()
        merge_use = merge_end - merge_start
        logger.info(f"合并结束,用时{merge_use}s")
    else:
        break_train = True

    # 卸载模型，清空cuda显存
    torch_gc()
    logger.info("已卸载模型")

    # 如果offload_folder存在，则删除
    if os.path.exists(offload_folder):
        shutil.rmtree(offload_folder)
        logger.info("已删除临时offload文件夹")

    reset_train_state()
    return train_use, merge_use, break_train


def torch_gc() -> None:
    r"""Collect the device memory."""
    global model, tokenizer, trainer
    del model, tokenizer, trainer
    gc.collect()
    if torch.xpu.is_available():
        torch.xpu.empty_cache()
    elif torch.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()


def tokenizer_function(samples, tokenizer, dataset_padding, dataset_max_length):
    texts = [f"{instruction}\n{input}\n{output}" for instruction, input, output in
             zip(samples["instruction"], samples["input"], samples["output"])]
    tokens = tokenizer(texts, truncation=True, padding=dataset_padding,
                       max_length=dataset_max_length)  # 使用批次中数据集的最大长度进行填充--显著减少显存占用
    tokens["labels"] = tokens["input_ids"].copy()  # 自回归模型的labels=input_ids,但是比input_ids慢一位(通过t-1个token预测第t个token)
    return tokens


def get_all_linear_layers(model) -> list:
    target_modules = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            # 提取模块名称（不含父级路径）
            module_name = name.split(".")[-1]
            if module_name not in target_modules and module_name != "lm_head":
                target_modules.append(module_name)
    return target_modules


def stop_train() -> None:
    if is_training():
        train_callback.train_state = False


def is_training() -> bool:
    return train_callback.train_state


def reset_train_state() -> None:
    train_callback.train_state = False


if __name__ == '__main__':
    train(model_path=r"E:\models\Qwen\Qwen3-0.6B", torch_dtype=torch.bfloat16,
          dataset_path=r"E:\datasets\Brain_teasers\data.json", train_output_dir="./result",
          lora_save_dir="./lora", fin_tuning_merge_dir="./final", num_train_epochs=30, logging_steps=5)
