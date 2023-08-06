# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manuscriptmonitor']

package_data = \
{'': ['*']}

install_requires = \
['PySimpleGUI>=4.47.0,<5.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.1,<2.0.0',
 'rich>=11.2.0,<12.0.0',
 'watchdog>=2.1.6,<3.0.0']

setup_kwargs = {
    'name': 'manuscriptmonitor',
    'version': '0.1.0',
    'description': 'a tool for keeping a ongoing CaptureOne tethered workflow in sync with a guide sheet',
    'long_description': None,
    'author': 'David Flood',
    'author_email': 'davidfloodii@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
