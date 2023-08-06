# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hodgepodge', 'hodgepodge.cli', 'hodgepodge.cli.command_groups']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.0.3,<1.1.0',
 'click>=7.0,<8.0',
 'psutil>=5.8.0,<6.0.0',
 'python-dateutil>=2.7.3,<2.8.0',
 'requests>=2.22.0,<2.23.0',
 'setuptools>=45.2.0,<45.3.0',
 'stix2>=3.0.1,<4.0.0',
 'taxii2-client>=2.3.0,<3.0.0',
 'urllib3>=1.25.8,<1.26.0']

entry_points = \
{'console_scripts': ['hodgepodge = hodgepodge.cli:cli']}

setup_kwargs = {
    'name': 'hodgepodge',
    'version': '3.3.5',
    'description': '',
    'long_description': "# hodgepodge  \n\n[![](https://img.shields.io/pypi/pyversions/hodgepodge)](https://pypi.org/project/hodgepodge/) [![](https://img.shields.io/pypi/wheel/hodgepodge)](https://pypi.org/project/hodgepodge/#files) [![](https://img.shields.io/pypi/l/hodgepodge)](https://github.com/whitfieldsdad/hodgepodge/blob/main/LICENSE.md)\n\n> _A **hodgepodge** of hopefully helpful helper code_\n\n![These are a few of my favourite functions](https://raw.githubusercontent.com/whitfieldsdad/images/main/a-few-of-my-favourite-things.jpg)\n\n## FAQ\n\n### What can it do?\n\n- Search for files and directories;\n- Hash files;\n- Pack files into archives;\n- Perform pattern matching;\n- Compress and decompress objects;\n- Parse dates and times;\n- Read STIX 2.0 objects from local files, directories, or TAXII servers;\n- Make the outputs from your tools more human-readable; and\n- ✨ More ✨.\n\nSupported hash algorithms:\n- MD5\n- SHA-1\n- SHA-256\n- SHA-512\n\nSupported archive formats:\n- ZIP\n\nSupported compression algorithms:\n- GZIP\n\n## Installation\n\nTo install `hodgepodge` using `pip`:\n\n```shell\n$ pip install hodgepodge\n```\n\nTo install `hodgepodge` from source (requires [`poetry`](https://github.com/python-poetry/poetry)):\n\n```shell\n$ git clone git@github.com:whitfieldsdad/hodgepodge.git\n$ cd hodgepodge\n$ make install\n```\n\nTo install `hodgepodge` from source using `setup.py` (i.e. if you're not using `poetry`):\n\n```shell\n$ git clone git@github.com:whitfieldsdad/hodgepodge.git\n$ cd hodgepodge\n$ python3 setup.py install\n```\n\n## Testing\n\nYou can run the unit tests for this package as follows:\n\n```shell\n$ make test\n```\n\nA code coverage report will automatically be written to: `htmlcov/index.html`.\n\nOn Linux systems, you can use `xdg-open` to open this file using the system's default web browser:\n\n```shell\n$ xdg-open htmlcov/index.html\n```\n",
    'author': 'Tyler Fisher',
    'author_email': 'tylerfisher@tylerfisher.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whitfieldsdad/hodgepodge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.0,<4',
}


setup(**setup_kwargs)
