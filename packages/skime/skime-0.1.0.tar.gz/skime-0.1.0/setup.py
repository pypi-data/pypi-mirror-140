# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skime', 'skime.compiler', 'skime.types']

package_data = \
{'': ['*'], 'skime': ['scheme/*']}

install_requires = \
['PyYAML>=5,<6']

setup_kwargs = {
    'name': 'skime',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7,<2.8',
}


setup(**setup_kwargs)
