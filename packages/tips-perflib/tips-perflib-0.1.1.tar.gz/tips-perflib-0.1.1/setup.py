# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tips_perflib']

package_data = \
{'': ['*']}

install_requires = \
['more-itertools>=8.12.0,<9.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'pymongo>=4.0.1,<5.0.0',
 'requests>=2.27.1,<3.0.0',
 'scipy>=1.8.0,<2.0.0',
 'types-requests>=2.27.11,<3.0.0']

setup_kwargs = {
    'name': 'tips-perflib',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Vlad Rachev',
    'author_email': 'vlad.rachev@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
