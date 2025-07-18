import argparse
from jllama import __version__


def main():
    parser = argparse.ArgumentParser(description='jllama-cli')

    # 可选参数（带短选项和长选项）
    parser.add_argument('-v', '--version', help='jllama版本')

    args = parser.parse_args()

    _version = args.version
    if _version:
        print(__version__)
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
