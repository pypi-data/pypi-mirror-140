# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['asttrs']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.8.1,<0.9.0',
 'attrs>=21.2.0,<22.0.0',
 'black>=21.9b0,<22.0',
 'cattrs>=1.8.0,<2.0.0',
 'isort>=5.9.3,<6.0.0']

setup_kwargs = {
    'name': 'asttrs',
    'version': '0.4.6',
    'description': 'A attrs-style wrapper for python ast',
    'long_description': '# asttrs\nA attrs-style wrapper for python ast\n',
    'author': 'ryanchao2012',
    'author_email': 'ryanchao2012@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ryanchao2012/asttrs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
