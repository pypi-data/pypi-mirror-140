# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geraldo3', 'geraldo3.generators']

package_data = \
{'': ['*']}

install_requires = \
['PyPDF3>=1.0.5,<2.0.0', 'reportlab>=3.6.3,<4.0.0']

setup_kwargs = {
    'name': 'geraldo3',
    'version': '0.1.0',
    'description': 'Python 3 version of reportgenerator Geraldo by Marinho Brandao based of ReportLab. Not  ready for production',
    'long_description': None,
    'author': 'Nico de Groot',
    'author_email': 'ndegroot0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
