# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skillmap']

package_data = \
{'': ['*'], 'skillmap': ['themes/*']}

install_requires = \
['toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['skillmap = skillmap.main:main']}

setup_kwargs = {
    'name': 'skillmap',
    'version': '0.2.2',
    'description': 'Skillmap generates a skill tree from a toml file',
    'long_description': None,
    'author': 'Yue Ni',
    'author_email': 'niyue.com@gmail.com',
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
