# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['outline_vpn_api_client',
 'outline_vpn_api_client.http',
 'outline_vpn_api_client.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'outline-vpn-api-client',
    'version': '0.1.0',
    'description': 'An async Python wrapper for Outline VPN API',
    'long_description': None,
    'author': 'geo_madness',
    'author_email': 'andrewsalt.e@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
