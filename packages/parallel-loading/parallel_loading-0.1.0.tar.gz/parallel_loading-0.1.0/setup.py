# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parallel_loading']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'parallel-loading',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'p208p2002',
    'author_email': 'p208p2002@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
