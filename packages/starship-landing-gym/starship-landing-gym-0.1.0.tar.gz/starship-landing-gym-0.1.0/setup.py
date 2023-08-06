# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starship_landing_gym', 'starship_landing_gym.envs']

package_data = \
{'': ['*']}

install_requires = \
['gym==0.19.0', 'numpy==1.21.5', 'pyglet>=1.5.21,<2.0.0']

setup_kwargs = {
    'name': 'starship-landing-gym',
    'version': '0.1.0',
    'description': 'A Gym env for rocket landing.',
    'long_description': None,
    'author': 'Armandpl',
    'author_email': 'adpl33@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
