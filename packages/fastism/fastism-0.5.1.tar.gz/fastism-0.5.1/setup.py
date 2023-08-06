# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastism', 'fastism.models']

package_data = \
{'': ['*']}

install_requires = \
['pydot>=1.4.1,<2.0.0', 'tensorflow>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'fastism',
    'version': '0.5.1',
    'description': 'Fast In-silico Mutagenesis for Convolution-based Neural Networks',
    'long_description': None,
    'author': 'Surag Nair',
    'author_email': 'surag@stanford.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
