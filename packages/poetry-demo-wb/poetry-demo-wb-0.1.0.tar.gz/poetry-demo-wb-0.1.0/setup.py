# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_demo_wb']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0']

entry_points = \
{'console_scripts': ['poetry-demo-wb = poetry_demo_wb.console:main']}

setup_kwargs = {
    'name': 'poetry-demo-wb',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Will Beresford',
    'author_email': 'Will.Beresford@YASA.com',
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
