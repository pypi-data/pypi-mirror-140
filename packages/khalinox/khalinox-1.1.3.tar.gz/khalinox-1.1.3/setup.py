# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['khalinox']

package_data = \
{'': ['*']}

install_requires = \
['JayDeBeApi>=1.2.3,<2.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'hdfs>=2.6.0,<3.0.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.1,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'toolz>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'khalinox',
    'version': '1.1.3',
    'description': '',
    'long_description': None,
    'author': 'Khalid',
    'author_email': 'khalid.chakhmoun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
