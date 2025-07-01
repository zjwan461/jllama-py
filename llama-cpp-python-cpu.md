## 本地构建安装
1. 安装cpu版本不用安装Visual Studio, 下载`MinGw64`并解压。[下载链接](https://github.com/niXman/mingw-builds-binaries/releases)。 假如安装在E:/software/mingw64路径下
2. 执行如下命令进行安装

```shell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
$env:CMAKE_ARGS = "-DGGML_OPENBLAS=on -DCMAKE_C_COMPILER=E:/software/mingw64/bin/gcc.exe -DCMAKE_CXX_COMPILER=E:/software/mingw64/bin/g++.exe"
pip install llama-cpp-python[server]
```

## 使用预编译whl文件安装
目前llama-cpp-python官方提供的cpu版预编译whl版本只到[v0.3.2](https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.2/llama_cpp_python-0.3.2-cp311-cp311-win_amd64.whl)

