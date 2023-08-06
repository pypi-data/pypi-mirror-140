# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_examples']

package_data = \
{'': ['*']}

install_requires = \
['eagerx>=0.1.2,<0.2.0',
 'h5py>=2.9.0,<3.0.0',
 'pyglet>=1.5.21,<2.0.0',
 'stable-baselines3==1.1.0']

setup_kwargs = {
    'name': 'eagerx-examples',
    'version': '0.1.3',
    'description': 'Code examples of EAGERx.',
    'long_description': None,
    'author': 'Bas van der Heijden',
    'author_email': 'd.s.vanderheijden@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eager-dev/eagerx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
