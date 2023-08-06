# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['namer']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.8.0,<5.0.0',
 'mutagen>=1.45.1,<2.0.0',
 'pathvalidate>=2.5.0,<3.0.0',
 'rapidfuzz>=2.0.5,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'schedule>=1.1.0,<2.0.0',
 'watchdog>=2.1.6,<3.0.0']

setup_kwargs = {
    'name': 'namer',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': '4c0d3r',
    'author_email': '4c0d3r@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
