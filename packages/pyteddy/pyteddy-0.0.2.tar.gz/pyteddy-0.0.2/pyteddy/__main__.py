from . import get_template
from .templates import releif_template

import argparse
from string import Template
from os import mkdir
from venv import EnvBuilder
from pathlib import Path
from pprint import PrettyPrinter
import sys
import traceback

VERSION = '0.0.2'


def match(command, *args, **kwargs):
    try:
        return getattr(sys.modules[__name__], command.replace('-', '_'))
    except:
        print('unknown command')
        sys.exit(1)

def version(*args, **kwargs):
    print('v' + VERSION)


def create_directory(releived_template, path, mapping):
    path.mkdir()

    for name, content in releived_template.items():
        if type(content) is dict:
            create_directory(content, path / name, mapping)
        else:
            create_file(content, path / name)


def create_file(content, path):
    path.touch()
    file = path.open('w')
    file.write(content)


def create_package(args):
    mapping = vars(args)
    env_builder = EnvBuilder()
    env_builder.create(mapping['package_name'])
    package_path = Path(mapping['package_name']) / Path(mapping['package_name'])
    template = get_template('default_package_template')
    content = releif_template(template, mapping)
    create_directory(content, package_path, mapping)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pyteddy', description='pyhon project manager')
    parser.add_argument('--version', '-v', help='get version', action='store_true')
    subparsers = parser.add_subparsers(help='subparsers', dest='command')
    create_package_parser = subparsers.add_parser('create-package', help='creates a package')
    create_package_parser.add_argument('--package-name', help='package name', required=True)
    create_package_parser.add_argument('--user-name', help='User\'s name', required=True)
    create_package_parser.add_argument('--user-email', help='User\'s email', required=True)
    create_package_parser.add_argument('--organisation', help='Github repostiory\'s organisation', required=True)
    create_package_parser.add_argument('--repository-name', help='Github repostory name', required=True)
    create_package_parser.add_argument('--verbose', '-v', help='enable verbose error messages', action='store_true')
    create_package_parser.add_argument('--year', '-y', help='year used to releif template')

    args = parser.parse_args()
    print(args)
    verbose = False
    if vars(args).get('verbose'):
        verbose = True
        vars(args).pop('verbose')

    try:
        if vars(args).get('version'):
            vars(args).pop('version')
            version()
        elif args.command is None:
            parser.parse_args(['--help'])
        else:
            match(args.command)(args)
    except Exception as e:
        print('Fail! an error has occured.')
        if vars(args).get('verbose'):
            traceback.print_exception(Exception, e, sys.exc_info()[2])
        else:
            print('Try again with --verbose to see python stack trace.')
