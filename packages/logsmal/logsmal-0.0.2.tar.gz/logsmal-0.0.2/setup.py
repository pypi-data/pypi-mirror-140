# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logsmal', 'logsmal.independent']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'logsmal',
    'version': '0.0.2',
    'description': 'Создание файлов конфигураци',
    'long_description': '',
    'author': 'Denis Kustov',
    'author_email': 'denis-kustov@rambler.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/denisxab/logsmal.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
