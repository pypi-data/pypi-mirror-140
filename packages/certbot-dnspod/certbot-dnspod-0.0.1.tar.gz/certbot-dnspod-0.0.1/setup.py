# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['certbot_dnspod']

package_data = \
{'': ['*']}

install_requires = \
['certbot>=1.23.0,<2.0.0',
 'dnspod-sdk>=0.0.2,<0.0.3',
 'zope.interface>=5.4.0,<6.0.0']

setup_kwargs = {
    'name': 'certbot-dnspod',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'codeif',
    'author_email': 'me@codeif.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
