# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cpa']

package_data = \
{'': ['*']}

install_requires = \
['adjustText', 'anndata>=0.7.5', 'scvi-tools>=0.14.6,<0.15.0']

extras_require = \
{':(python_version < "3.8") and (extra == "docs")': ['typing_extensions'],
 ':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'dev': ['black>=20.8b1',
         'codecov>=2.0.8',
         'flake8>=3.7.7',
         'isort>=5.7',
         'jupyter>=1.0',
         'loompy>=3.0.6',
         'nbconvert>=5.4.0',
         'nbformat>=4.4.0',
         'pre-commit>=2.7.1',
         'pytest>=4.4',
         'scanpy>=1.6'],
 'docs': ['ipython>=7.1.1',
          'nbsphinx',
          'nbsphinx-link',
          'pydata-sphinx-theme>=0.4.0',
          'scanpydoc>=0.5',
          'sphinx>=3.0,<4.0',
          'sphinx-autodoc-typehints',
          'sphinx-rtd-theme'],
 'tutorials': ['leidenalg',
               'loompy>=3.0.6',
               'python-igraph',
               'scanpy>=1.6',
               'scikit-misc>=0.1.3']}

setup_kwargs = {
    'name': 'cpa-tools',
    'version': '0.1.0',
    'description': 'Compositional Perturbation Autoencoder (CPA)',
    'long_description': 'CPA\n',
    'author': 'Mohsen Naghipourfar',
    'author_email': 'naghipourfar@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/cpa/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<4.0',
}


setup(**setup_kwargs)
