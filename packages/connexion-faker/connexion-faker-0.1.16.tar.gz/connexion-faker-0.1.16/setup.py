# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['connexion_faker']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=11.3.0,<12.0.0', 'connexion>=2.9.0,<3.0.0']

extras_require = \
{'aiohttp': ['aiohttp>=3.0,<4.0', 'aiohttp_jinja2>=1.0,<2.0'],
 'django': ['Django<=4.0.2', 'django-connexion>=0.0.1,<0.0.2']}

setup_kwargs = {
    'name': 'connexion-faker',
    'version': '0.1.16',
    'description': 'Auto-generate mocks from your Connexion API using OpenAPI',
    'long_description': None,
    'author': 'Erle Carrara',
    'author_email': 'carrara.erle@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
