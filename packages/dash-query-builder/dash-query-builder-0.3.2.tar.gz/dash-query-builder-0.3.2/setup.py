# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dash_query_builder']

package_data = \
{'': ['*']}

install_requires = \
['dash>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'dash-query-builder',
    'version': '0.3.2',
    'description': 'Dash Component based on react-awesome-query-builder',
    'long_description': None,
    'author': 'Tyler Baur',
    'author_email': 'baur.tyler@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
