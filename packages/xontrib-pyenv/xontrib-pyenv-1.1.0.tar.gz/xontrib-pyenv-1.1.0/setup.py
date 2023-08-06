# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xontrib_pyenv']

package_data = \
{'': ['*']}

install_requires = \
['xontrib-langenv>=1.0.6,<2.0.0']

setup_kwargs = {
    'name': 'xontrib-pyenv',
    'version': '1.1.0',
    'description': 'Skeleton for `xontrib-pyenv`. This package is deprecated, please use `xontrib-langenv` instead.',
    'long_description': '# xontrib-pyenv\n\nPredecessor of `xontrib-langenv`, deprecated.\n\nIf you are using this project, please update to [xontrib-langenv](https://github.com/dyuri/xontrib-langenv)!\n',
    'author': 'Gyuri Horak',
    'author_email': 'dyuri@horak.hu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dyuri/xontrib-pyenv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
