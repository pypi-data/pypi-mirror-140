# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['lookie = src.lookie:main']}

setup_kwargs = {
    'name': 'lookie',
    'version': '0.1.9',
    'description': 'lookie is the tool to help you monitor different kind of resources.',
    'long_description': '# lookie\n`lookie` is the tool to help you monitor different kind of resources.\n',
    'author': 'fahadahammed',
    'author_email': 'iamfahadahammed@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
