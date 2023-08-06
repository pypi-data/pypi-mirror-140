# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_reality']

package_data = \
{'': ['*']}

install_requires = \
['eagerx>=0.1.2,<0.2.0']

setup_kwargs = {
    'name': 'eagerx-reality',
    'version': '0.1.2',
    'description': 'Simple bridge that can be used in reality together with several useful nodes.',
    'long_description': None,
    'author': 'Jelle Luijkx',
    'author_email': 'j.d.luijkx@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eager-dev/eagerx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
