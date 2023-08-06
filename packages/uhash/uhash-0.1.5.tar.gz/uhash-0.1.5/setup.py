# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uhash']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome==3.10.1']

setup_kwargs = {
    'name': 'uhash',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'NamTH',
    'author_email': 'namth2302@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
