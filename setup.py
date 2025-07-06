# setup.py
from setuptools import setup, find_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


def get_requires() -> list[str]:
    with open("requirements.txt", encoding="utf-8") as f:
        file_content = f.read()
        lines = [line.strip() for line in file_content.strip().split("\n") if not line.startswith("#")]
        return lines


setup(
    name='jllama-py',
    version='1.1.2',
    url='https://github.com/zjwan461/jllama-py',
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=get_requires(),
    entry_points={
        'console_scripts': [
            'jllama = jllama.main:main',  # 格式：'命令名 = 模块名.函数名:函数入口'
        ],
    },
    package_data={
        # 包含 jllama 包中的所有 HTML 文件
        'jllama': ['ui/dist/**', 'templates/**', 'nav.json', 'ext/llama_cpp/**', 'logging.conf'],
    },
    # 其他元数据
    author='Jerry',
    author_email='826935261@qq.com',
    description='A simple AI Tool set application',
    long_description=readme(),
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='gguf AI huggingface modelscope pytorch transformers llama_cpp llamafactory',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",  # Windows系统
        "Programming Language :: Python :: 3.11",
    ],
)
