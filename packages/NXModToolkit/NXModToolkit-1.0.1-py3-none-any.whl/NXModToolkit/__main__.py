import sys

import argparse

from NXModToolkit import creator, packager


def main():
    parser = argparse.ArgumentParser(description='Toolkit for creating and packaging .nxmod files.')
    subparsers = parser.add_subparsers()
    creator_parser = subparsers.add_parser('create', help='Create a new project.')
    packager_parser = subparsers.add_parser('package', help='Package a project.')
    packager_parser.add_argument('path', help='Path to the project.')
    creator_parser.set_defaults(func=creator.run)
    packager_parser.set_defaults(func=packager.run)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
