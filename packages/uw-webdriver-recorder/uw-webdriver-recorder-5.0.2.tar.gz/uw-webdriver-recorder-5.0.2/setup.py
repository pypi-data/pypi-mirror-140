# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webdriver_recorder']

package_data = \
{'': ['*'], 'webdriver_recorder': ['templates/*', 'templates/static/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pytest>=6.2.4,<7.0.0',
 'selenium>=4.1.0,<5.0.0']

entry_points = \
{'pytest11': ['uw-webdriver-recorder = webdriver_recorder.plugin']}

setup_kwargs = {
    'name': 'uw-webdriver-recorder',
    'version': '5.0.2',
    'description': 'A pytest plugin for recording screenshots of selenium interactions, with other convenient features too.',
    'long_description': None,
    'author': 'Tom Thorogood',
    'author_email': 'goodtom@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
