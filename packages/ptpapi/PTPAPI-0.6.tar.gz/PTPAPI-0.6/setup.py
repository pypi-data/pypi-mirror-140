# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ptpapi', 'ptpapi.scripts', 'ptpapi.sites']

package_data = \
{'': ['*']}

install_requires = \
['Tempita>=0.5.2,<0.6.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'bencode.py>=4.0.0,<5.0.0',
 'guessit>=3.4.3,<4.0.0',
 'humanize>=4.0.0,<5.0.0',
 'pyrosimple>=1.1.0,<2.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['ptp = ptpapi.scripts.ptp:main',
                     'ptp-reseed = ptpapi.scripts.ptp_reseed:main',
                     'ptp-reseed-machine = '
                     'ptpapi.scripts.ptp_reseed_machine:main']}

setup_kwargs = {
    'name': 'ptpapi',
    'version': '0.6',
    'description': 'A small API for a mildly popular movie site',
    'long_description': None,
    'author': 'kannibalox',
    'author_email': 'kannibalox@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kannibalox/PTPAPI',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
