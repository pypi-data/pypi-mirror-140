import argparse
import sys

from kAuto.create import create


def main():
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    parser = argparse.ArgumentParser(description="自动化测试框架")
    parser.add_argument("-v", "--version", help="版本号", action="store_true")
    parser.add_argument("-i", "--init", help="初始化项目", action="store_true")
    args = parser.parse_args()
    if args.version:
        print("1.2")
    if args.init:
        try:
            create()
        except:
            pass


if __name__ == "__main__":
    main()
