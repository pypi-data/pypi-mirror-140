# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ectocet']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'ectocet',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'guillaumervls',
    'author_email': '3765057+guillaumervls@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
