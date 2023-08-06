# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strarting_apache2_from_linode_server']

package_data = \
{'': ['*']}

install_requires = \
['linode-api4>=5.2.1,<6.0.0',
 'requests>=2.27.1,<3.0.0',
 'secure-smtplib>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['monitor_script = '
                     'strarting_apache2_from_linode_server.monitor:main']}

setup_kwargs = {
    'name': 'strarting-apache2-from-linode-server',
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
