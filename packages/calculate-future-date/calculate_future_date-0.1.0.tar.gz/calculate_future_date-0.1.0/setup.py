# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calculate_future_date']

package_data = \
{'': ['*']}

install_requires = \
['Flask==2.0.3', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['my_calc = calculate_future_date.mycalc:calc_future']}

setup_kwargs = {
    'name': 'calculate-future-date',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'pratik kumar sarangi',
    'author_email': 'psarangi50@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
