from .. import get_template
from ..templates import releif_template

from venv import EnvBuilder
from pathlib import Path
import requests

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


def create_package(mapping):
    if Path(mapping['package_name']).is_file():
        raise FileExistsError()
    if mapping.get('repository_name') is None:
        mapping['repository_name'] = mapping.get('package_name')

    if len(mapping.get('user_name').split(' ')) == 1:
        print("Warning: Surname not detected")

    env_builder = EnvBuilder()
    env_builder.create(mapping['package_name'])
    package_path = Path(mapping['package_name']) / Path(mapping['package_name'])
    template = get_template('default_package_template')
    content = releif_template(template, mapping)
    create_directory(content, package_path, mapping)
    try:
        pypi_statuscode = requests.get(releif_template('https://pypi.org/pypi/$package_name/json', mapping)).status_code 
        if pypi_statuscode == 200:
            print('Warning: package already exists on pypi')
        elif pypi_statuscode != 404:
            print(f'Warning: could not check pypi - error {pypi_statuscode}')
            
    except:
        print('Warning: could not check pypi - error unknown')

    