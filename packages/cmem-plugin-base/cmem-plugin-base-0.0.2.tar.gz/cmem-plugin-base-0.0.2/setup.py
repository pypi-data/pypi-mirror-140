# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cmem_plugin_base', 'cmem_plugin_base.dataintegration']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cmem-plugin-base',
    'version': '0.0.2',
    'description': 'Base classes for developing eccenca Coporate Memory plugins.',
    'long_description': '# cmem-plugin-base\n\nPython base classes for developing eccenca Coporate Memory plugins.\n\n',
    'author': 'eccenca',
    'author_email': 'cmempy-developer@eccenca.com',
    'maintainer': 'Sebastian Tramp',
    'maintainer_email': 'sebastian.tramp@eccenca.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
