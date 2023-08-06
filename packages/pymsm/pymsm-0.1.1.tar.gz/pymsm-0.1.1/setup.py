# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pymsm', 'pymsm.archive', 'pymsm.datasets', 'pymsm.examples']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.1.0,<2.0.0',
 'lifelines>=0.26.4,<0.27.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'scikit-survival>=0.17.0,<0.18.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'pymsm',
    'version': '0.1.1',
    'description': 'Multstate modeling',
    'long_description': None,
    'author': 'Hagai Rossman, Ayya Keshet',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
