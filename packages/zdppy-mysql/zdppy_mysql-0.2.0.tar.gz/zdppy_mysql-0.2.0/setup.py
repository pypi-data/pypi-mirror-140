# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdppy_mysql']

package_data = \
{'': ['*']}

install_requires = \
['aiomysql>=0.0.22,<0.0.23', 'zdppy-log>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'zdppy-mysql',
    'version': '0.2.0',
    'description': '使用python操作MySQL,同时支持同步版本和异步版本,支持事务',
    'long_description': None,
    'author': 'zhangdapeng',
    'author_email': 'pygosuperman@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
