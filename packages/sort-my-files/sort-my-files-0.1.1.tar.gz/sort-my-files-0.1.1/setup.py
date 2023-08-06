# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sort_my_files']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['sort-my-files = sort_my_files.main:app']}

setup_kwargs = {
    'name': 'sort-my-files',
    'version': '0.1.1',
    'description': '',
    'long_description': '',
    'author': 'Daniel Evans',
    'author_email': 'me@daredoes.work',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
