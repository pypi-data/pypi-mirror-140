# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pwnkss']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['pwnkss = pwnkss.new:main']}

setup_kwargs = {
    'name': 'pwnkss',
    'version': '0.1.1',
    'description': 'Just a package built by pawan at TAI',
    'long_description': None,
    'author': 'pawanniroula777',
    'author_email': 'pawanniroula777@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
