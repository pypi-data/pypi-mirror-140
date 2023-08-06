# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vnpy_sinopac', 'vnpy_sinopac.gateway']

package_data = \
{'': ['*']}

install_requires = \
['shioaji>=0.3.4-alpha.1,<0.4.0']

setup_kwargs = {
    'name': 'vnpy-sinopac',
    'version': '1.0.6',
    'description': 'The best trading API - Shioaji gateway with VNPY.',
    'long_description': None,
    'author': 'ypochien',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
