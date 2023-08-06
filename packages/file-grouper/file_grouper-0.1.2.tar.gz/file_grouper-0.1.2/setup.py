# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_grouper']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0']

entry_points = \
{'console_scripts': ['group_file = file_grouper.file_grouper:group_file',
                     'hello = file_grouper.console:hello']}

setup_kwargs = {
    'name': 'file-grouper',
    'version': '0.1.2',
    'description': 'Group file based on file name pattern defined by regex.',
    'long_description': '# Usage\n\nI use this script to group beestar maths worksheet\n\n```\npipx install file-grouper\ngroup_file --no-dryrun --key_regex "(grade_03_.*)_\\d\\d" --group_no 1 --dst_root grade3_group\\ grade3\\*\n```\n\n# Setup Dev Environment\n\nFirst clone this repo then change to the repo directory.\n\nThen run following command:\n```sh\npip install poetry\npoetry install   # Create virtual environement, install all dependencies for the project\npoetry shell     # activate the virtual environment\npre-commit install    # to ensure automatically formatting, linting, type checking and testing before every commit\n```\n\nIf you want to run unit test manually, just activate virtual environment and run:\n```sh\npytest\n```',
    'author': 'Yu Wang',
    'author_email': 'anselmwang@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/anselmwang/file_grouper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
