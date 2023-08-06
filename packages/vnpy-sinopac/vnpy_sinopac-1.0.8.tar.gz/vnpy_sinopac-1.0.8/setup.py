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
    'version': '1.0.8',
    'description': 'The best trading API - Shioaji gateway with VNPY.',
    'long_description': '[![GitHub license](https://img.shields.io/github/license/ypochien/vnpy_sinopac)](https://github.com/ypochien/vnpy_sinopac/blob/main/LICENSE)\n[![GitHub issues](https://img.shields.io/github/issues/ypochien/vnpy_sinopac?style=plastic)](https://github.com/ypochien/vnpy_sinopac/issues)\n![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/ypochien/vnpy_sinopac/Deploy?event=push)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vnpy_sinopac)\n![PyPI](https://img.shields.io/pypi/v/vnpy_sinopac)\n\nVeighNa框架的 Sinopac 交易接口\n\n- VeighNa (VNPY) - https://github.com/vnpy/vnpy/\n- shioaji - https://sinotrade.github.io/',
    'author': 'ypochien',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ypochien/vnpy_sinopac',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
