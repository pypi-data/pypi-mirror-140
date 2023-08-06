# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['evops', 'evops.metrics', 'evops.utils']

package_data = \
{'': ['*']}

install_requires = \
['nptyping>=1.4.4,<2.0.0', 'numpy>=1.21.5,<2.0.0', 'open3d>=0.14.1,<0.15.0']

setup_kwargs = {
    'name': 'evops',
    'version': '0.1.0',
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
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
