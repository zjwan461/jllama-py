# setup.py
from setuptools import setup, find_packages

setup(
    name='jllama',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        # 列出你的项目依赖
        'pywebview==5.4',
        'flask==3.1.1',
        'flask-cors==6.0.1',
        'requests==2.32.3',
        'psutil==7.0.0',
        'GPUtil==1.4.0',
        'SQLAlchemy==2.0.41',
        'modelscope==1.26.0',
        'orjson==3.10.18',
        'transformers==4.52.4',
        'accelerate==1.7.0',
        'addict==2.4.0',
        'WMI==1.5.1',
        'hf_xet==1.1.5',
        'torch~=2.7.1',
        'numpy~=1.26.4',
        'tqdm~=4.67.1',
        'sentencepiece~=0.2.0',
        'pyyaml~=6.0.2',
        'huggingface-hub~=0.33.0',
        'uvicorn~=0.34.3',
        'datasets~=3.6.0',
        'bitsandbytes~=0.46.0',
        'peft~=0.15.2',
        'safetensors~=0.5.3',
        'jinja2~=3.1.6',
        'paramiko~=3.5.1',
        'scp~=0.15.0',
        'llamafactory~=0.9.3'
    ],
    entry_points={
        'console_scripts': [
            'jllama = jllama.main:main',  # 格式：'命令名 = 模块名.函数名:函数入口'
        ],
    },
    package_data={
        # 包含 jllama 包中的所有 HTML 文件
        'jllama': ['ui/dist/**', 'templates/**', 'nav.json'],
    },
    # 其他元数据
    author='Jerry',
    author_email='826935261@qq.com',
    description='A simple AI Tool set application',
    license='MIT',
    keywords='gguf AI huggingface modelscope pytorch transformers llama_cpp llamafactory',
)
