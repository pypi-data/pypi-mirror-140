# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ddmtools', 'ddmtools.image', 'ddmtools.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'colorcet>=3.0.0,<4.0.0',
 'ipywidgets>=7.6.5,<8.0.0',
 'joblib>=1.1.0,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'lmfit>=1.0.3,<2.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numba>=0.55.1,<0.56.0',
 'numdifftools>=0.9.40,<0.10.0',
 'numpy==1.20.3',
 'opencv-python',
 'pandas>=1.3.4,<2.0.0',
 'statsmodels>=0.13.1,<0.14.0',
 'tqdm>=4.62.3,<5.0.0',
 'typing-extensions>=4.1.1,<5.0.0',
 'uncertainties>=3.1.6,<4.0.0']

setup_kwargs = {
    'name': 'ddmtools',
    'version': '0.3.0',
    'description': 'A Python library for doing differential dynamic microscopy on polydisperse samples',
    'long_description': None,
    'author': 'Jeppe Klitgaard',
    'author_email': 'jk782@cam.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JeppeKlitgaard/DDMTools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
