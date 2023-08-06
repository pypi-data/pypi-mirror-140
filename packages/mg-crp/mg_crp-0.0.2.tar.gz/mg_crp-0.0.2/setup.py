# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mg_crp']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodomex>=3.14.1,<4.0.0']

setup_kwargs = {
    'name': 'mg-crp',
    'version': '0.0.2',
    'description': 'Создание файлов конфигураци',
    'long_description': '',
    'author': 'Denis Kustov',
    'author_email': 'denis-kustov@rambler.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/denisxab/mg_crp.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
