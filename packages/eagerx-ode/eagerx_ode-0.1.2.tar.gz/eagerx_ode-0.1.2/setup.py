# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_ode']

package_data = \
{'': ['*']}

install_requires = \
['eagerx>=0.1.2,<0.2.0', 'scipy>=1.5.4,<2.0.0']

setup_kwargs = {
    'name': 'eagerx-ode',
    'version': '0.1.2',
    'description': 'Bridge (with corresponding nodes) that uses arbitrary ODEs to simulate objects in EAGERx.',
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
