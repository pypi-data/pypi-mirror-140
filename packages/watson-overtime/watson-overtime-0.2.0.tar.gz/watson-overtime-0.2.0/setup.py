# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['watson_overtime']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<=9.0.0', 'humanize>=3.14.0,<5.0.0', 'pytimeparse>=1.1.8,<2.0.0']

extras_require = \
{':python_version <= "3.7"': ['importlib-metadata==4.2.0']}

entry_points = \
{'console_scripts': ['watson-overtime = watson_overtime.main:main']}

setup_kwargs = {
    'name': 'watson-overtime',
    'version': '0.2.0',
    'description': 'Check overtime in combination with the td-watson time tracker',
    'long_description': None,
    'author': 'Joris Clement',
    'author_email': 'flyingdutchman@posteo.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/flyingdutchman23/watson-overtime',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
