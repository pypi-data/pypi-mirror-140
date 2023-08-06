# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['web3storage']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'web3storage',
    'version': '0.1.1',
    'description': 'Interacting with the web3.storage API to upload/download files',
    'long_description': None,
    'author': 'Marcus Weinberger',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
