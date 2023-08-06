# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['damnsshmanager', 'damnsshmanager.ssh']

package_data = \
{'': ['*'], 'damnsshmanager': ['damnfiles/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'paramiko>=2.8.0,<3.0.0',
 'sshtunnel>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['dsm = damnsshmanager.cli:main']}

setup_kwargs = {
    'name': 'damnsshmanager',
    'version': '0.2.4',
    'description': 'The simplest ssh cli agent one is able to find',
    'long_description': None,
    'author': 'Nils Verheyen',
    'author_email': 'nils@ungerichtet.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
