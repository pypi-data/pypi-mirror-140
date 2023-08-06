# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cython_packages']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.7,<0.30.0', 'numpy>=1.16,<2.0']

setup_kwargs = {
    'name': 'cython-packages',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Stefan Kjartansson',
    'author_email': 'esteban.supreme@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
