# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grpc_boilerplate',
 'grpc_boilerplate.grpcio_aio_tools',
 'grpc_boilerplate.grpcio_tools',
 'grpc_boilerplate.grpclib_tools']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'grpc-boilerplate',
    'version': '0.10',
    'description': '',
    'long_description': None,
    'author': 'Dmirty Simonov',
    'author_email': 'demalf@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
