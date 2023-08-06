# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['broadway', 'broadway.examples', 'broadway.siRNA', 'broadway.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'broadway',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'jfwu-ai',
    'author_email': 'junfeng.wu@ainnocence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
