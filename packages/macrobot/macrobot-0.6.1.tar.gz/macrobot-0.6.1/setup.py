# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['macrobot', 'macrobot.tests']

package_data = \
{'': ['*']}

install_requires = \
['MarkupSafe==2.0.1',
 'jinja2==2.10.3',
 'numpy==1.18.3',
 'opencv-python==4.2.0.34',
 'pytest==5.4.1',
 'scikit-image==0.16.2']

entry_points = \
{'console_scripts': ['mb = macrobot.cli:main']}

setup_kwargs = {
    'name': 'macrobot',
    'version': '0.6.1',
    'description': 'Macrobot is an image analysis software for studying plant-pathogen interactions on macroscopic level.',
    'long_description': None,
    'author': 'Stefanie Lueck',
    'author_email': 'lueck@ipk-gatersleben.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
