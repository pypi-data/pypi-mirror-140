# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfinra', 'pyfinra.financials', 'pyfinra.financials.tools']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.1,<2.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'pyfinra',
    'version': '0.2.0',
    'description': 'unofficial Finra api',
    'long_description': None,
    'author': 'T-136',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
