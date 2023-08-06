# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['huichao_poetry_demo']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'urllib3>=1.26.8,<2.0.0']

setup_kwargs = {
    'name': 'huichao-poetry-demo',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'cheng-huichao',
    'author_email': 'cheng.huichao@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
