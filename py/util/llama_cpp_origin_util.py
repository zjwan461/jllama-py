import os
import platform
import subprocess


def merge_gguf(input_file_path: str, output_file_path):
    cpp_dir = check_cpp_dir()
    split_exe = os.path.join(cpp_dir, "llama-gguf-split")
    cmd = [split_exe, "--merge", input_file_path, output_file_path]
    with subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        for line in proc.stderr:
            yield f"{line.strip()}\n"
        for line in proc.stdout:
            yield f"{line.strip()}\n"


def split_gguf(input_file_path: str, output_file_path: str, options: dict):
    cpp_dir = check_cpp_dir()
    split_exe = os.path.join(cpp_dir, "llama-gguf-split")
    cmd = [split_exe, "--split"]
    if len(options) > 0:
        if "--split-max-size" in options:
            split_max_size = options["--split-max-size"]
            cmd_options = ["--split-max-size", split_max_size]
            cmd = cmd + cmd_options
        elif "--split-max-tensors" in options:
            split_max_tensors = options["--split-max-tensors"]
            cmd_options = ["--split-max-tensors", split_max_tensors]
            cmd = cmd + cmd_options

    cmd.append(input_file_path)
    cmd.append(output_file_path)
    with subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            yield f"{line.strip()}\n"


def check_cpp_dir():
    work_dir = os.getcwd()
    cpp_dir = os.path.join(work_dir, "ext/llama_cpp/" + platform.system())
    if not os.path.exists(cpp_dir):
        raise Exception("can not found ext llama_cpp path")
    return cpp_dir


def quantize(input_file_path: str, output_file_path: str, q_type):
    if q_type not in supported_q_type():
        raise Exception(f"not supported quantize type: {q_type}")
    cpp_dir = check_cpp_dir()
    quantize_exe = os.path.join(cpp_dir, "llama-quantize")
    cmd = [quantize_exe, input_file_path, output_file_path, q_type]
    with subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            yield f"{line.strip()}\n"


def supported_q_type():
    return [
        "Q4_0",
        "Q4_1",
        "Q5_0",
        "Q5_1",
        "IQ2_XXS",
        "IQ2_XS",
        "IQ2_S",
        "IQ2_M",
        "IQ1_S",
        "IQ1_M",
        "TQ1_0",
        "TQ2_0",
        "Q2_K",
        "Q2_K_S",
        "IQ3_XXS",
        "IQ3_S",
        "IQ3_M",
        "Q3_K",
        "IQ3_XS",
        "Q3_K_S",
        "Q3_K_M",
        "Q3_K_L",
        "IQ4_NL",
        "IQ4_XS",
        "Q4_K",
        "Q4_K_S",
        "Q4_K_M",
        "Q5_K",
        "Q5_K_S",
        "Q5_K_M",
        "Q6_K",
        "Q8_0",
        "F16",
        "BF16",
        "F32",
        "COPY"
    ]
