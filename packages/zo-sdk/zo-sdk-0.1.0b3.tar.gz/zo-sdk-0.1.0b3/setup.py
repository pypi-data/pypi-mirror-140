# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zo']

package_data = \
{'': ['*']}

install_requires = \
['anchorpy>=0.7.0,<0.8.0', 'solana>=0.21.0,<0.22.0']

setup_kwargs = {
    'name': 'zo-sdk',
    'version': '0.1.0b3',
    'description': '01.xyz Python SDK',
    'long_description': None,
    'author': 'Sheheryar Parvaz',
    'author_email': 'me@cherryman.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
