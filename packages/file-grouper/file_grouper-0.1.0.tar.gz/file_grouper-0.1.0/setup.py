# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_grouper']

package_data = \
{'': ['*']}

install_requires = \
['pre-commit>=2.17.0,<3.0.0']

entry_points = \
{'console_scripts': ['group_file = file_grouper.file_grouper:group_file',
                     'hello = file_grouper.console:hello']}

setup_kwargs = {
    'name': 'file-grouper',
    'version': '0.1.0',
    'description': 'Group file based on file name pattern defined by regex.',
    'long_description': None,
    'author': 'Yu Wang',
    'author_email': 'anselmwang@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
