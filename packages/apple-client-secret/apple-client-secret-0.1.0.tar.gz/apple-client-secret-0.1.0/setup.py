# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['apple_client_secret']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['generate-secret = apple_client_secret.main:cli']}

setup_kwargs = {
    'name': 'apple-client-secret',
    'version': '0.1.0',
    'description': 'Generate a client_secret for Apple Sign-in',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
