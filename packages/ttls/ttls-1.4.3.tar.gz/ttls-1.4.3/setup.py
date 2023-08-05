# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ttls']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.3,<4.0.0', 'colour>=0.1.5,<0.2.0']

entry_points = \
{'console_scripts': ['ttls = ttls.cli:main']}

setup_kwargs = {
    'name': 'ttls',
    'version': '1.4.3',
    'description': 'Twinkly Twinkly Little Star',
    'long_description': '# Twinkly Twinkly Little Star\n\n`ttls` is a small package to help you make async requests to Twinkly LEDs. A command line tool (also called `ttls`) is also included, as well as some examples how to create both loadable movies and realtime sequences.\n\nWritten based on the [excellent XLED documentation](https://xled-docs.readthedocs.io/en/latest/) by [@scrool](https://github.com/scrool).\n',
    'author': 'Jakob Schlyter',
    'author_email': 'jakob@schlyter.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jschlyter/ttls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
