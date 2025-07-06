## 本地构建安装

如果之前安装过cpu版本的llama-cpp-python,请先执行 
```shell
pip uninstall llama-cpp-python -y
pip cache purge 
```
之后重新执行cuda版本安装命令

### 开始安装

1. 安装`Visual Studio 2022`软件并安装`C++运行环境`, 比如安装在`F:\software\Microsoft Visual Studio\xxxx` 目录下
2. 安装[cuda](https://developer.nvidia.com/cuda-downloads), 一般安装在`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9`目录下。如果找不到cuda安装目录，可以在系统环境变量中找`CUDA_PATH`配置的路径
3. 将cuda目录下的`extras\visual_studio_integration\MSBuildExtensions`文件夹中的所有文件copy到`Visual Studio`目录下的`MSBuild\Microsoft\VC\v170\BuildCustomizations`文件夹中
4. 执行如下命令进行安装

```shell
$env:CMAKE_ARGS = "-DGGML_CUDA=ON -DCUDAToolkit_ROOT='F:\software\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VC\v170\BuildCustomizations'"
pip install llama-cpp-python[server]
```

## 使用预编译whl文件安装
[Releases · abetlen/llama-cpp-python](https://github.com/abetlen/llama-cpp-python/releases)

下载对应的cuda版本的whl后进行安装