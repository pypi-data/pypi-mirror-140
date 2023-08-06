# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vnpy_sinopac', 'vnpy_sinopac.gateway']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.1,<2.0.0', 'shioaji']

setup_kwargs = {
    'name': 'vnpy-sinopac',
    'version': '1.1.0',
    'description': 'The best trading API - Shioaji gateway with VNPY.',
    'long_description': '[![GitHub license](https://img.shields.io/github/license/ypochien/vnpy_sinopac)](https://github.com/ypochien/vnpy_sinopac/blob/main/LICENSE)\n[![GitHub issues](https://img.shields.io/github/issues/ypochien/vnpy_sinopac?style=plastic)](https://github.com/ypochien/vnpy_sinopac/issues)\n![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/ypochien/vnpy_sinopac/Deploy?event=push)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vnpy_sinopac)\n![PyPI](https://img.shields.io/pypi/v/vnpy_sinopac)\n\n# Shioaji API - Shioaji 交易接口 for VeighNa框架\n\n- Sinopac API - shioaji - https://sinotrade.github.io/\n- VeighNa (VNPY) - https://github.com/vnpy/vnpy/\n\n## Requirement\n* VeighNa 3.0 \n* Python 3.8 / 3.7 (建議用 Anaconda)\n## Installation\n```\npip install vnpy_sinopac\n```\n## Quickstarts\n```\npython scripy/run.py\n```\n\n## 關於下單方式\n### 股票\n\n\n### 期權\n\n\n\n## 贊助 Donating\n* 如果你發現這個專案有幫助到你，請考慮 [贊助](https://etherscan.io/address/ypochien.eth)\n* ETH是最棒的，但其他TOKEN也都歡迎。\n\n\n\n',
    'author': 'ypochien',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ypochien/vnpy_sinopac',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
