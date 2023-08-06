# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['myrepos']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0']

entry_points = \
{'console_scripts': ['my-repos = myrepos.repos:cli']}

setup_kwargs = {
    'name': 'my-repos',
    'version': '0.1.1',
    'description': 'Keep an offline mirror of some git repositories',
    'long_description': None,
    'author': 'xtofl',
    'author_email': 'kristoffel.pirard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
