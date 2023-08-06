# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brain_cli']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['brain = brain_cli.main:app']}

setup_kwargs = {
    'name': 'brain-cli',
    'version': '0.1.0',
    'description': 'Brainshare CLI https://brainshare.io',
    'long_description': '# Brainshare CLI\n\nhello cli world',
    'author': 'Zachary King',
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
