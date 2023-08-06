# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cython_packages']

package_data = \
{'': ['*']}

modules = \
['__init__']
setup_kwargs = {
    'name': 'cython-packages',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'NamTH',
    'author_email': 'namth2302@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'python_requires': '>=3.6.2,<4.0.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
