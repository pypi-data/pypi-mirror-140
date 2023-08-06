# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fifa98edit']

package_data = \
{'': ['*'], 'fifa98edit': ['FifaStyles/*']}

install_requires = \
['colorama>=0.4.4,<0.5.0',
 'numpy>=1.19.0,<2.0.0',
 'pandas>=1.0.5,<2.0.0',
 'pillow>=7.2.0,<8.0.0',
 'unidecode>=1.3.2,<2.0.0']

extras_require = \
{':sys_platform == "win32"': ['pypiwin32>=223,<224']}

setup_kwargs = {
    'name': 'fifa98edit',
    'version': '0.1.21',
    'description': 'A command-line database editor for FIFA RTWC 98.',
    'long_description': None,
    'author': 'Megas Alexandros',
    'author_email': 'megas_alexandros@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ma-akad/fifa98edit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
