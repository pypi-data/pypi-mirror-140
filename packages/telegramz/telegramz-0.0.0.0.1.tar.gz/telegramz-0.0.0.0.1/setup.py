# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'telegramz'}

packages = \
['tgz']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'telegramz',
    'version': '0.0.0.0.1',
    'description': '',
    'long_description': '<img src=https://shields-io-visitor-counter.herokuapp.com/badge?page=https://pypi.org/project/telegramz/=purple&style=flat-square>\n\n',
    'author': 'saner99',
    'author_email': 'it@saner99.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
