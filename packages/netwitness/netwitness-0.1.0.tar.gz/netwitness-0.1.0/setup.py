# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netwitness']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'motor>=2.5.1,<3.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'netwitness',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sean Drzewiecki',
    'author_email': 'sean.drzewiecki@netwitness.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)
