# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hotfinger', 'hotfinger.finger_handle_tools']

package_data = \
{'': ['*'],
 'hotfinger': ['.git/*',
               '.git/hooks/*',
               '.git/info/*',
               '.git/logs/*',
               '.git/logs/refs/heads/*',
               '.git/objects/04/*',
               '.git/objects/11/*',
               '.git/objects/27/*',
               '.git/objects/3c/*',
               '.git/objects/45/*',
               '.git/objects/46/*',
               '.git/objects/47/*',
               '.git/objects/59/*',
               '.git/objects/5c/*',
               '.git/objects/62/*',
               '.git/objects/70/*',
               '.git/objects/71/*',
               '.git/objects/77/*',
               '.git/objects/7f/*',
               '.git/objects/80/*',
               '.git/objects/83/*',
               '.git/objects/8b/*',
               '.git/objects/92/*',
               '.git/objects/b7/*',
               '.git/objects/bd/*',
               '.git/objects/be/*',
               '.git/objects/e8/*',
               '.git/objects/e9/*',
               '.git/objects/ee/*',
               '.git/objects/f9/*',
               '.git/objects/fc/*',
               '.git/objects/fe/*',
               '.git/refs/heads/*',
               'data/*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'loguru>=0.6.0,<0.7.0',
 'lxml>=4.8.0,<5.0.0',
 'python-Wappalyzer>=0.3.1,<0.4.0',
 'webanalyzer>=2019.8.22,<2020.0.0']

setup_kwargs = {
    'name': 'hotfinger',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'zmf96',
    'author_email': 'zmf96@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
