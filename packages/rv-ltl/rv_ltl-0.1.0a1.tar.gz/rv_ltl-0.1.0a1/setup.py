# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rv_ltl']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rv-ltl',
    'version': '0.1.0a1',
    'description': '',
    'long_description': None,
    'author': 'Shun',
    'author_email': 'shunthedev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
