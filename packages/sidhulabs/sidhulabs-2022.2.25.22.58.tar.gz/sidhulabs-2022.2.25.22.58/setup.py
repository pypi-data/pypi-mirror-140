# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sidhulabs', 'sidhulabs.database', 'sidhulabs.elastic']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.31,<2.0.0',
 'elasticsearch>=8,<9',
 'loguru>=0.6.0,<0.7.0',
 'pyodbc>=4.0.32,<5.0.0']

setup_kwargs = {
    'name': 'sidhulabs',
    'version': '2022.2.25.22.58',
    'description': 'Common Python utility functions',
    'long_description': None,
    'author': 'Ashton Sidhu',
    'author_email': 'ashton.sidhu1994@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
