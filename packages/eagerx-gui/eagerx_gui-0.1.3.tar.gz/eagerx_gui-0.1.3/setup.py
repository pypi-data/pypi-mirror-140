# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagerx_gui', 'eagerx_gui.templates']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.6,<6.0.0',
 'eagerx>=0.1.2,<0.2.0',
 'opencv-python==4.3.0.36',
 'pyqtgraph>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'eagerx-gui',
    'version': '0.1.3',
    'description': 'GUI to visualise graphs in EAGERx.',
    'long_description': None,
    'author': 'Jelle Luijkx',
    'author_email': 'j.d.luijkx@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eager-dev/eagerx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
