# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bqsc']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'mypy>=0.910,<0.911',
 'pandas-gbq>=0.17.1,<0.18.0',
 'pandas>=1.3.4,<2.0.0']

entry_points = \
{'console_scripts': ['bqsc = bqsc.cli:main']}

setup_kwargs = {
    'name': 'bqsc',
    'version': '5.0.0',
    'description': 'Define schema object from bigquery schema definition json file',
    'long_description': None,
    'author': 'Yasunori Horikoshi',
    'author_email': 'hotoku@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
