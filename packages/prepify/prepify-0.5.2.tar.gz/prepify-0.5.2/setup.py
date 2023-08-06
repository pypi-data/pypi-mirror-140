# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prepify', 'prepify.py']

package_data = \
{'': ['*'], 'prepify': ['resources/prepdoc_template.docx']}

install_requires = \
['PySimpleGUI>=4.57.0,<5.0.0',
 'XlsxWriter>=3.0.3,<4.0.0',
 'natsort>=8.1.0,<9.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.1,<2.0.0',
 'python-docx>=0.8.11,<0.9.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'prepify',
    'version': '0.5.2',
    'description': 'a tool for recording data from the physical examination of a New Testament manuscript',
    'long_description': None,
    'author': 'David Flood',
    'author_email': 'davidfloodii@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
