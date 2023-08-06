# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycordrest']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.3,<3.0.0', 'py-cord>=1.7.3,<2.0.0']

setup_kwargs = {
    'name': 'pycordrest',
    'version': '0.1.0',
    'description': 'The REST API for py-cord',
    'long_description': 'Py-cord REST ext\n\nExample in example.py file\n\nLICENSE : MIT',
    'author': 'InfiniteCore',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/InfiniteCore/pycordrest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
