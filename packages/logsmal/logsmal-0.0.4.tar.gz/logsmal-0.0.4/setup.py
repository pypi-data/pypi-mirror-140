# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logsmal', 'logsmal.independent']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'logsmal',
    'version': '0.0.4',
    'description': 'Создание файлов конфигураци',
    'long_description': '## Использование\n\n```python\nfrom logsmal import logger\n\nlogger.success("Программа запущена", flag="RUN")\n```\n\nСоздать кастомный логгер. Посмотрите все доступные аргменты :meth:`logsmal.loglevel.__init__()`\n\n```python\nfrom logsmal import loglevel, logger, CompressionLog\n\nlogger.MyLogger = loglevel(\n    level="[melogger]",\n    fileout="./log/mylog.log",\n    max_size_file="10kb",\n    console_out=False,\n    compression=CompressionLog.zip_file\n)\n```',
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
