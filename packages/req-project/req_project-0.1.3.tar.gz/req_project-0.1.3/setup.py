# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['req_project', 'req_project.commands', 'req_project.tools']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.26,<4.0.0',
 'MarkupSafe>=2.0.1,<3.0.0',
 'Pillow>=9.0.0,<10.0.0',
 'lxml>=4.7.1,<5.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.0,<2.0.0',
 'passlib>=1.7.4,<2.0.0',
 'pexpect>=4.8.0,<5.0.0',
 'platformdirs>=2.4.1,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'strictdoc>=0.0.18,<0.0.19',
 'svgwrite>=1.4.1,<2.0.0',
 'textX>=2.3.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'winapps>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'req-project',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Michael Naderhirn',
    'author_email': 'm.naderhirn@nmrobotic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
