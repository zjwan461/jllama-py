import argparse
import sys

from jllama import __version__


def main():
    parser = argparse.ArgumentParser(description='jllama-cli')

    parser.add_argument('-v', '--version', action="version", version=f'jllama {__version__}', help='jllama版本')

    parser.add_argument('-s', '--serve', action="store_true", help='启动jllama')

    args = parser.parse_args()

    if args.serve:
        from jllama.main import main as serve
        serve()
    else:
        parser.print_usage(
            sys.stderr
        )


if __name__ == '__main__':
    main()
