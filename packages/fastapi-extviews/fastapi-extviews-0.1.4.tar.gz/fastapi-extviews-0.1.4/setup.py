# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extviews']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.73', 'motor>=2.0', 'pymongo>=3.11']

setup_kwargs = {
    'name': 'fastapi-extviews',
    'version': '0.1.4',
    'description': 'extviews is a fastapi library for creating RESTful APIs with a single class.',
    'long_description': '# Fastapi-ExtViews\n\nextviews is a fastapi library for creating RESTful APIs with classes.\n',
    'author': 'Bilal Alpaslan',
    'author_email': 'm.bilal.alpaslan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BilalAlpaslan/fastapi-extviews',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
