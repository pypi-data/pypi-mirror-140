# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yaoauth2', 'yaoauth2.providers']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.72.0,<0.73.0',
 'httpx>=0.21.3,<0.22.0',
 'nxtools>=1.6,<2.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'yaoauth2',
    'version': '0.0.1',
    'description': 'Simple OAuth2 client library for FastAPI',
    'long_description': None,
    'author': 'Martin Wacker',
    'author_email': 'martas@imm.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
