# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['solana_pay',
 'solana_pay.common',
 'solana_pay.common.utils',
 'solana_pay.core',
 'solana_pay.core.models',
 'solana_pay.core.transactions',
 'solana_pay.core.transactions.builders',
 'solana_pay.core.transactions.validators']

package_data = \
{'': ['*']}

install_requires = \
['solana>=0.21.0,<0.22.0']

setup_kwargs = {
    'name': 'solana-pay-py',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'itayb1',
    'author_email': 'itay4445@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.2,<4.0.0',
}


setup(**setup_kwargs)
