# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netprot']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'netprot',
    'version': '0.1.0',
    'description': 'A system-indipendent network protocol manipulation and evaluation library.',
    'long_description': None,
    'author': 'Federico Olivieri',
    'author_email': 'lvrfrc87@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
