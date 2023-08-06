# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jambot_plugin', 'jambot_plugin.handlers']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.5.3,<2.0.0',
 'Jinja2>=3.0.3,<4.0.0',
 'aiodine>=1.2.9,<2.0.0',
 'croniter>=1.3.4,<2.0.0',
 'inflection>=0.5.1,<0.6.0',
 'jambot-client>=0.1.0,<0.2.0',
 'multidict>=6.0.2,<7.0.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'jambot-plugin',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Vladislav Bakaev',
    'author_email': 'vlad@bakaev.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
