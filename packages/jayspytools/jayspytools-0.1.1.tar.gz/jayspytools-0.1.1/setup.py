# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jayspytools']

package_data = \
{'': ['*']}

install_requires = \
['pyspark>=3.2.1,<4.0.0']

setup_kwargs = {
    'name': 'jayspytools',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'jaygovind-sahu',
    'author_email': 'jaygovind.sahu@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
