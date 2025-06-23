from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = r"D:\models\models--uer--gpt2-chinese-cluecorpussmall\snapshots\c2c0249d8a2731f269414cc3b22dff021f8e07a3"

model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("-----------模型加载成功--------------")

# 准备数据集
from datasets import load_dataset
