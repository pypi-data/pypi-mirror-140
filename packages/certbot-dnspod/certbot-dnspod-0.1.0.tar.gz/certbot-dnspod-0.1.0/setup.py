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

entry_points = \
{'certbot.plugins': ['certbot-dnspod = certbot_dnspod:Authenticator']}

setup_kwargs = {
    'name': 'certbot-dnspod',
    'version': '0.1.0',
    'description': 'A certbot plugin for DNSPod',
    'long_description': '# certbot-dnspod\n\nA certbot plugin for DNSPod\n\n## 安装\n\n```\npip install certbot-dnspod\n```\n\n## 创建证书\n\n```\nsudo certbot certonly \\\n--authenticator certbot-dnspod \\\n--certbot-dnspod-credentials ~/.secrets/certbot/dnspod.ini \\\n-d example.com \\\n-d *.myfunpinpin.com\n```\n\n其中~/.secrets/certbot/dnspod.ini为配置文件路径，内容\n\n```\ncertbot_dnspod_token_id = <your token id>\ncertbot_dnspod_token = <your token>\n```\n\nchmod\n\n```\nchmod 600 ~/.secrets/certbot/dnspod.ini\n```\n\n## 参数\n\n官方插件是参数形式是\n```\n--dns-cloudflare-credentials\n```\n\n而第三方插件的参数是::\n\n```\n--authenticator certbot-dnspod\n```\n\n或者\n\n```\n-a certbot-dnspod\n```\n\n## 其他\n\n- [certbot命令行参数](https://eff-certbot.readthedocs.io/en/stable/using.html#certbot-command-line-options)\n- [编写一个certbot插件](https://certbot.eff.org/docs/contributing.html#writing-your-own-plugin)\n- [官方插件](https://certbot.eff.org/docs/using.html#dns-plugins)\n- [三方插件](https://certbot.eff.org/docs/using.html#third-party-plugins)\n- [poetry加自定义的entry_points](https://python-poetry.org/docs/pyproject/#plugins)\n\n',
    'author': 'codeif',
    'author_email': 'me@codeif.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codeif/certbot-dnspod',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
