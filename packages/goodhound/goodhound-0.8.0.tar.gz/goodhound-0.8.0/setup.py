# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['goodhound']

package_data = \
{'': ['*']}

install_requires = \
['pandas==1.3.5', 'py2neo==2021.2.3']

entry_points = \
{'console_scripts': ['goodhound = goodhound:main']}

setup_kwargs = {
    'name': 'goodhound',
    'version': '0.8.0',
    'description': 'Attackers think in graphs, defenders think in actions, management think in charts.  GoodHound operationalises Bloodhound by determining the busiest paths to high value targets and creating actionable output to prioritise remediation of attack paths.',
    'long_description': None,
    'author': 'Andi Morris',
    'author_email': 'andi.morris@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
