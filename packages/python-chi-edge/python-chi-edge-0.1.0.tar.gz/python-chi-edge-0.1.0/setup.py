# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chi_edge', 'chi_edge.vendor.FATtools']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.1,<9.0.0',
 'keystoneauth1>=4.4.0,<5.0.0',
 'python-chi>=0.15.4,<0.16.0',
 'rich>=11.2.0,<12.0.0']

entry_points = \
{'console_scripts': ['chi-edge = chi_edge.cli:cli']}

setup_kwargs = {
    'name': 'python-chi-edge',
    'version': '0.1.0',
    'description': 'Manage edge devices for use with the CHI@Edge IoT/Edge testbed.',
    'long_description': None,
    'author': 'Chameleon Project',
    'author_email': 'contact@chameleoncloud.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
