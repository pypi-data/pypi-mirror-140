# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_dcsc_setups',
 'eagerx_dcsc_setups.mops',
 'eagerx_dcsc_setups.mops.ode',
 'eagerx_dcsc_setups.mops.real']

package_data = \
{'': ['*']}

install_requires = \
['eagerx-gui>=0.1.3,<0.2.0',
 'eagerx-ode>=0.1.2,<0.2.0',
 'eagerx-reality>=0.1.2,<0.2.0',
 'eagerx>=0.1.2,<0.2.0',
 'stable-baselines3==1.0']

setup_kwargs = {
    'name': 'eagerx-dcsc-setups',
    'version': '0.1.4',
    'description': 'EAGERx interface to dcsc_setups.',
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
