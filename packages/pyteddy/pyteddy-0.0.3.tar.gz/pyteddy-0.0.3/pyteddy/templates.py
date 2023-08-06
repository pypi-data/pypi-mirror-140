from string import Template


def releif_template(template, mapping):
    if type(template) is dict:
        releived_template = {}
        for name, content in template.items():
            releived_template[releif_template(name, mapping)] = releif_template(content, mapping)
        
        return releived_template
    
    if type(template) is tuple:
        return releif_template('\n'.join(template) + '\n', mapping)
    
    return Template(template).substitute(mapping)
        

_default_package_template = {
    '$package_name': {
        '__init__.py': '',
    },
    'tests': {
        '__init__.py': ('import unittest', 'import $package_name')
    },
    '.gitignore': ('__pycache__/', '*.egg-info/', 'build/'),
    'LICENSE': (
        'MIT License',
        '',
        'Copyright (c) 2022 $user_name',
        '',
        'Permission is hereby granted, free of charge, to any person obtaining a copy',
        'of this software and associated documentation files (the "Software"), to deal',
        'in the Software without restriction, including without limitation the rights',
        'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell',
        'copies of the Software, and to permit persons to whom the Software is',
        'furnished to do so, subject to the following conditions:',
        '',
        'The above copyright notice and this permission notice shall be included in all'
        'copies or substantial portions of the Software.',
        '',
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
        'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,'
        'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE',
        'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER'
        'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,'
        'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE'
        'SOFTWARE.',
    ),
    'pyproject.toml': (
        '[build-system]',
        'requires = [',
        '"setuptools>=42",',
        '"wheel"',
        ']',
        'build-backend = "setuptools.build_meta"',
    ),
    'README.md': ('### $package_name',),
    'requirements.txt': (),
    'setup.cfg': (
        '[metadata]',
        'name = $package_name',
        'version = 0.0.0',
        'author = $user_name',
        'author_email = $user_email',
        'description = summary',
        'long_description = file: README.md',
        'long_description_content_type = text/markdown',
        'url = https://github.com/$organisation/$repository_name',
        'project_urls =',
        'Bug Tracker = https://github.com/$organisation/$repository_name/issues',
        'classifiers =',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        '',
        '[options]',
        'package_dir =',
        '    = .',
        'packages = find:',
        'python_requires = >=3.9',
        '',
        '[options.packages.find]',
        'where = .',
    ),
}