# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['namewiz']

package_data = \
{'': ['*']}

install_requires = \
['PySimpleGUI>=4.57.0,<5.0.0']

setup_kwargs = {
    'name': 'namewiz',
    'version': '0.1.0',
    'description': 'a tool for generating the filename for a CSNTM CaptureOne session',
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
