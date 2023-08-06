# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['es_orm']

package_data = \
{'': ['*']}

install_requires = \
['elasticsearch==7.10.0']

setup_kwargs = {
    'name': 'es-orm',
    'version': '0.1.1',
    'description': 'easy es helper',
    'long_description': None,
    'author': 'iulmt',
    'author_email': '1817556010@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
