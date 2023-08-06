# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pqr', 'pqr.core', 'pqr.factors', 'pqr.metrics', 'pqr.tests']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=8.0.0,<9.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.0,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'scipy>=1.8.0,<2.0.0',
 'statsmodels>=0.13.1,<0.14.0']

setup_kwargs = {
    'name': 'pqr',
    'version': '0.4.1',
    'description': '',
    'long_description': None,
    'author': 'Andrey Babkin',
    'author_email': 'andrey.babkin.ru71@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
