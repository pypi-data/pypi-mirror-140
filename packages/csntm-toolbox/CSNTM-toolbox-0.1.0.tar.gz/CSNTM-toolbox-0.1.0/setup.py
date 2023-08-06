# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['csntm_toolbox']

package_data = \
{'': ['*']}

install_requires = \
['ManuscriptMonitor>=0.1.0,<0.2.0',
 'NameWiz>=0.1.0,<0.2.0',
 'prepify>=0.5.0,<0.6.0']

setup_kwargs = {
    'name': 'csntm-toolbox',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'David Flood',
    'author_email': 'davidfloodii@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
