# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vlan_change']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0',
 'netmiko>=3.4.0,<4.0.0',
 'python-dotenv>=0.19.2,<0.20.0']

entry_points = \
{'console_scripts': ['vlanchange = vlan_change.cli:cli']}

setup_kwargs = {
    'name': 'vlan-change',
    'version': '0.1.0',
    'description': 'Simple program to change vlans on ports',
    'long_description': None,
    'author': 'Angelo Poggi',
    'author_email': 'angelo.poggi@opti9tech.com',
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
