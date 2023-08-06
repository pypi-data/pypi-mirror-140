# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cmem_plugin_examples', 'cmem_plugin_examples.workflow']

package_data = \
{'': ['*']}

install_requires = \
['cmem-plugin-base>=0.0.2,<0.0.3']

setup_kwargs = {
    'name': 'cmem-plugin-examples',
    'version': '0.0.2',
    'description': 'Example plugins for eccenca Corporate Memory.',
    'long_description': '# cmem-plugin-examples\n\nExample plugins using cmem-plugin-base.\n',
    'author': 'eccenca',
    'author_email': 'cmempy-developer@eccenca.com',
    'maintainer': 'Sebastian Tramp',
    'maintainer_email': 'sebastian.tramp@eccenca.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
