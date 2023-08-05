# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pymsm', 'pymsm.archive', 'pymsm.datasets', 'pymsm.examples']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel>=6.9.1,<7.0.0',
 'joblib>=1.1.0,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'lifelines>=0.26.4,<0.27.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scikit-survival>=0.17.0,<0.18.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'pymsm',
    'version': '0.1.0',
    'description': 'Multistate modelling on python',
    'long_description': '![PyPI](https://img.shields.io/pypi/v/pymsm)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/pymsm)\n[![Run tests](https://github.com/hrossman/pymsm/actions/workflows/tests.yml/badge.svg)](https://github.com/hrossman/pymsm/actions/workflows/tests.yml)  \n\n# PyMSM\nPython implemantation of Multistate competing risk models.\n\n## Installation\n`pip install pymsm`\n\n## Usage examples\n[First example](https://github.com/hrossman/pymsm/blob/main/src/pymsm/examples/first_example.ipynb)  \n[EBMT example](https://github.com/hrossman/pymsm/blob/main/src/pymsm/examples/ebmt.ipynb)\n\n\n## Resources  \n[Original R code repository](https://github.com/JonathanSomer/covid-19-multi-state-model)  \n[Roimi et. al. Methods supplementary](https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/jamia/28/6/10.1093_jamia_ocab005/1/ocab005_supplementary_data.pdf?Expires=1643875060&Signature=jEb1TAvDfCw7w3YZ4M1N1hy~BZN1J38RCOLtAmhEY14pASyoQPX9F51ne-5WmRd9oKWn-m52~GGhsy5RnpAIpt0VmnoDmCEA51a1lpnsxn-nt~suKCA2mM2ldM7nPb31xAnFTpX638cob3bGMc3vlj3WKxpLDIUuAqF2lmQf0h5cXeeJXLW1NOAyjlHn1Xj387oSs~vQJfjJ7dwKEVH6M3mtKf1tELJo9CRkSMJuDBApoL7lCgeeM9PuJDT-SHwH9debf10Sk5QvbelLWJpSwSU35ifMEpHxqXputuoPj0z9tdmzjkSXDGN2wIucNnUa9mloF8eNCOWLhYqHjusTPg__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA)  \n[R mstate package tutorial](https://cran.r-project.org/web/packages/mstate/vignettes/Tutorial.pdf)\n',
    'author': 'Hagai Rossman',
    'author_email': 'hagairossman@gmail.com>, Ayya Keshet <ayya.keshet@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hrossman/pymsm',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
