import argparse
import sys

from jllama import __version__
from jllama.util.update_util import update_version, update_other

parser = argparse.ArgumentParser(description='jllama-cli')


def main():
    # 走更新逻辑
    update_version()
    update_other()
    parser.add_argument('-v', '--version', action="version", version=f'jllama {__version__}', help='jllama版本')

    parser.add_argument('--serve', action="store_true", help='启动jllama')

    parser.add_argument('--list', action="store_true", help='列出本地模型')
    parser.add_argument('--search', action="store", help='搜索模型')
    parser.add_argument('--pull', nargs="+", type=str, action="store", help='下载模型')
    parser.add_argument('--show', action="store", help='查看模型详细信息')
    parser.add_argument('--primary', nargs=2, action="store", help='给模型的primary gguf打标')
    parser.add_argument('--run', action="store", help='运行模型')
    parser.add_argument('--ps', action="store_true", help='查看运行中的模型')
    parser.add_argument('--stop', action="store_true", help='停止推理进程')

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
    elif args.show:
        from jllama.controller.console_api import console_api
        console_api.show_model_info(args.show)
    elif args.primary:
        from jllama.controller.console_api import console_api
        console_api.mark_primary(args.primary)
    elif args.run:
        from jllama.controller.console_api import console_api
        console_api.run_model(args.run)
    elif args.ps:
        from jllama.controller.console_api import console_api
        console_api.ps_process()
    elif args.stop:
        from jllama.controller.console_api import console_api
        console_api.stop_model()
    else:
        parser.print_usage(
            sys.stderr
        )


if __name__ == '__main__':
    main()
