# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wj_pytrends']

package_data = \
{'': ['*']}

install_requires = \
['lxml==4.6.3', 'pandas==0.25.3', 'requests>=2.25.1']

setup_kwargs = {
    'name': 'wj-pytrends',
    'version': '1.0.5',
    'description': 'Whale&Jaguar Libary - Pytrends',
    'long_description': None,
    'author': 'Sebastian Franco',
    'author_email': 'jsfranco@whaleandjaguar.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6.1,<4.0',
}


setup(**setup_kwargs)
