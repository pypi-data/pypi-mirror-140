# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wapi2nsconf']

package_data = \
{'': ['*'], 'wapi2nsconf': ['templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'PyYAML>=5.3.1,<6.0.0',
 'requests>=2.25.0,<3.0.0',
 'urllib3>=1.26.2,<2.0.0',
 'voluptuous>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['wapi2nsconf = wapi2nsconf.cli:main']}

setup_kwargs = {
    'name': 'wapi2nsconf',
    'version': '0.4.0',
    'description': 'Infoblox WAPI to DNS server configuration tool',
    'long_description': None,
    'author': 'Jakob Schlyter',
    'author_email': 'jakob@kirei.se',
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
