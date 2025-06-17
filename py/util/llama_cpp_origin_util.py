import os
import platform
import subprocess


def merge_gguf(input_file_path: str, output_file_path):
    cpp_dir = check_cpp_dir()
    split_exe = os.path.join(cpp_dir, "llama-gguf-split")
    cmd = [split_exe, "--merge", input_file_path, output_file_path]
    with subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            yield f"{line.strip()}"


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
            yield f"{line.strip()}"


def check_cpp_dir():
    work_dir = os.getcwd()
    cpp_dir = os.path.join(work_dir, "ext/llama_cpp/" + platform.system())
    if not os.path.exists(cpp_dir):
        raise Exception("can not found ext llama_cpp path")
    return cpp_dir
