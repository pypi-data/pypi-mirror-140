# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minecraft_get_building']

package_data = \
{'': ['*']}

install_requires = \
['mcpi>=1.2.1,<2.0.0']

entry_points = \
{'console_scripts': ['minecraft_get_building = '
                     'minecraft_get_building.get_building_data:main']}

setup_kwargs = {
    'name': 'minecraft-get-building',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'konishi0125',
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
