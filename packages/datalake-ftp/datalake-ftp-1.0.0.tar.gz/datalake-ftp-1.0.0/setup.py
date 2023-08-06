# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datalake_ftp']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'datalake-framework>=1.0.1,<2.0.0',
 'pendulum>=2.1.2,<3.0.0']

entry_points = \
{'console_scripts': ['ftpcloud = datalake_ftp.cli:main']}

setup_kwargs = {
    'name': 'datalake-ftp',
    'version': '1.0.0',
    'description': 'Moves files from FTP drop folders to a Cloud Bucket',
    'long_description': '# Datalake File Transfer\n\nMoves files from FTP drop folders to a Cloud Bucket.\n',
    'author': 'Didier SCHMITT',
    'author_email': 'dschmitt@equancy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.equancy.cloud/equancy/data-technologies/datalake-ftp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
