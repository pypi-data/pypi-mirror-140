# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gaul', 'gaul.modelling', 'gaul.nn', 'gaul.optim', 'gaul.utils']

package_data = \
{'': ['*']}

install_requires = \
['jax>=0.3.1,<0.4.0', 'jaxlib>=0.3.0,<0.4.0', 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'gaul',
    'version': '0.1.0',
    'description': '',
    'long_description': 'Gaul\n======\n\n.. image:: https://img.shields.io/github/workflow/status/al-jshen/gaul/Tests?color=5E81AC&label=tests&style=for-the-badge\n  :target: https://github.com/al-jshen/gaul/actions?workflow=Tests\n\n.. image:: https://img.shields.io/codecov/c/github/al-jshen/gaul?color=62a69b&style=for-the-badge\n  :target: https://codecov.io/gh/al-jshen/gaul\n',
    'author': 'Jeff Shen',
    'author_email': 'jshen2014@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/al-jshen/gaul',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
