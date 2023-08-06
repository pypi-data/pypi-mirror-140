# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minecraftstatus']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'minecraftstatus',
    'version': '0.0.3',
    'description': 'minecraftstatus is an asynchronous wrapper for https://api.iapetus11.me.',
    'long_description': None,
    'author': 'Infernum1',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6',
}


setup(**setup_kwargs)
