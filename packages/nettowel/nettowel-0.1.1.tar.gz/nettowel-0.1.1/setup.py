# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nettowel', 'nettowel.cli']

package_data = \
{'': ['*']}

install_requires = \
['rich>=11.2.0,<12.0.0', 'ruamel.yaml>=0.17.21,<0.18.0', 'typer>=0.4.0,<0.5.0']

extras_require = \
{'full': ['Jinja2>=3.0.3,<4.0.0',
          'ttp>=0.8.4,<0.9.0',
          'textfsm>=1.1.2,<2.0.0',
          'napalm>=3.3.1,<4.0.0',
          'netmiko>=3.4.0,<4.0.0',
          'scrapli>=2022.1.30,<2023.0.0',
          'nornir>=3.2.0,<4.0.0'],
 'jinja': ['Jinja2>=3.0.3,<4.0.0', 'jinja2schema>=0.1.4,<0.2.0'],
 'napalm': ['napalm>=3.3.1,<4.0.0'],
 'netmiko': ['netmiko>=3.4.0,<4.0.0'],
 'nornir': ['nornir>=3.2.0,<4.0.0'],
 'scrapli': ['scrapli>=2022.1.30,<2023.0.0'],
 'textfsm': ['textfsm>=1.1.2,<2.0.0'],
 'ttp': ['ttp>=0.8.4,<0.9.0']}

entry_points = \
{'console_scripts': ['nettowel = nettowel.cli.main:run']}

setup_kwargs = {
    'name': 'nettowel',
    'version': '0.1.1',
    'description': 'Network Automation Collection',
    'long_description': None,
    'author': 'ubaumann',
    'author_email': 'github@m.ubaumann.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
