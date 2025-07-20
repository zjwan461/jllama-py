import argparse
import sys

from jllama import __version__

parser = argparse.ArgumentParser(description='jllama-cli')


def main():
    parser.add_argument('-v', '--version', action="version", version=f'jllama {__version__}', help='jllama版本')

    parser.add_argument('--serve', action="store_true", help='启动jllama')

    parser.add_argument('--list', action="store_true", help='列出本地模型')
    parser.add_argument('--search', action="store", help='搜索模型')
    parser.add_argument('--pull', nargs="+", type=str, action="store", help='下载模型')
    parser.add_argument('--run', action="store", help='运行模型')
    parser.add_argument('--stop', action="store", help='停止模型')
    parser.add_argument('--ps', action="store_true", help='列出正在运行的模型')

    args = parser.parse_args()

    if args.serve:
        from jllama.main import main as serve
        serve()
    elif args.list:
        from jllama.controller.console_api import console_api
        console_api.list_models()
    elif args.search:
        from jllama.util.modelscope_util import search_modelscope_model
        result = search_modelscope_model(args.search)
        if result.get("success"):
            total = result.get("total")
            output = f"founded {total} models\n"
            for item in result.get("models"):
                output += f"{item}\n"
            print(output)
    elif args.pull:
        from jllama.controller.console_api import console_api
        console_api.download_model(args.pull)
    else:
        parser.print_usage(
            sys.stderr
        )


if __name__ == '__main__':
    main()
