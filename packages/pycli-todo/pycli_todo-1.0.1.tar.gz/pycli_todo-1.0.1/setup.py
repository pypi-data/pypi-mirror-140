# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycli_todo']

package_data = \
{'': ['*']}

install_requires = \
['click-aliases>=1.0.1,<2.0.0', 'click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['td = pycli_todo.pytodo:entry_point']}

setup_kwargs = {
    'name': 'pycli-todo',
    'version': '1.0.1',
    'description': 'Simple to-do list for your terminal, made in Python',
    'long_description': None,
    'author': 'lufa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
