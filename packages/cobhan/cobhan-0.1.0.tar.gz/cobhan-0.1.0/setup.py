# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cobhan']

package_data = \
{'': ['*']}

install_requires = \
['cffi>=1.15.0,<2.0.0']

setup_kwargs = {
    'name': 'cobhan',
    'version': '0.1.0',
    'description': 'Cobhan FFI',
    'long_description': '# Cobhan FFI\n\nCobhan FFI is a proof of concept system for enabling shared code to be written in Rust or Go and consumed from all major languages/platforms in a safe and effective way, using easy helper functions to manage any unsafe data marshaling.\n\n## Types\n\n* Supported types\n    * int32 - 32bit signed integer\n    * int64 - 64bit signed integer\n    * float64 - double precision 64bit IEEE 754 floating point\n    * Cobhan buffer - length delimited 8bit buffer (no null delimiters)\n        * utf-8 encoded string\n        * JSON\n        * binary data \n* Cobhan buffer details\n    * Callers provide the output buffer allocation and capacity\n    * Called functions can transparently return larger values via temporary files\n    * **Modern [tmpfs](https://en.wikipedia.org/wiki/Tmpfs) is entirely memory backed**\n* Return values\n    * Functions that return scalar values can return the value directly\n        * Functions *can* use special case and return maximum positive or maximum negative or zero values to\n            represent error or overflow conditions\n        * Functions *can* allow scalar values to wrap\n        * Functions should document their overflow / underflow behavior\n\n',
    'author': 'Jeremiah Gowdy',
    'author_email': 'jeremiah@gowdy.me',
    'maintainer': 'GoDaddy',
    'maintainer_email': 'oss@godaddy.com',
    'url': 'https://github.com/godaddy/cobhan-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
