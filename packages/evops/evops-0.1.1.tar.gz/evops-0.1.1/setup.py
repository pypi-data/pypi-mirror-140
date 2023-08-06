# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['evops', 'evops.metrics', 'evops.utils']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata==4.8.3', 'nptyping>=1.4.4,<2.0.0', 'numpy>=1.19.0,<1.20.0']

setup_kwargs = {
    'name': 'evops',
    'version': '0.1.1',
    'description': 'Evaluation of Plane Segmentation.',
    'long_description': None,
    'author': 'Dmitriy Jarosh',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
