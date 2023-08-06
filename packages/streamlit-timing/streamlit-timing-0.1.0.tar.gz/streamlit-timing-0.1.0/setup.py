# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_timing']

package_data = \
{'': ['*']}

install_requires = \
['streamlit>=0.65.0']

setup_kwargs = {
    'name': 'streamlit-timing',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Yuichiro Tachibana (Tsuchiya)',
    'author_email': 't.yic.yt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
