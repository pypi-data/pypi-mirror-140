# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valtypes', 'valtypes.parsing', 'valtypes.parsing.parser', 'valtypes.util']

package_data = \
{'': ['*']}

install_requires = \
['regex>=2021.11.10,<2022.0.0']

setup_kwargs = {
    'name': 'valtypes',
    'version': '1.1.0',
    'description': 'A library for data parsing using Python type hints.',
    'long_description': '<p align="center">\n  <img src="https://raw.githubusercontent.com/LeeeeT/valtypes/main/docs/logo.png" alt="valtypes">\n</p>\n\n<p align="center">\n    <em>Nothing (almost) should ever be annotated as <b>any str</b> or <b>any int</b>.</em>\n</p>\n\n---\n\nWhat is valtypes?\n-----------------\n\n**Valtypes** is a library for data parsing using Python type hints.\n',
    'author': 'LeeeeT',
    'author_email': 'leeeet@inbox.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LeeeeT/valtypes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
