# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['response_measurer', 'response_measurer.tests']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['response-measurer = response_measurer.run:main']}

setup_kwargs = {
    'name': 'response-measurer',
    'version': '0.4.1',
    'description': 'A HTTP request response measurer',
    'long_description': None,
    'author': 'eminaktas',
    'author_email': 'eminaktas34@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
