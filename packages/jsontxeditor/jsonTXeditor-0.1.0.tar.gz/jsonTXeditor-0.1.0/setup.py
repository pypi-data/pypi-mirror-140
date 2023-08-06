# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsontxeditor']

package_data = \
{'': ['*']}

install_requires = \
['PySimpleGUI>=4.57.0,<5.0.0']

setup_kwargs = {
    'name': 'jsontxeditor',
    'version': '0.1.0',
    'description': 'a tool for editing JSON-formatted transcriptions files',
    'long_description': None,
    'author': 'David Flood',
    'author_email': 'davidfloodii@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
