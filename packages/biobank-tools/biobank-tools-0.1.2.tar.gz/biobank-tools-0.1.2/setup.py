# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biobank', 'tests']

package_data = \
{'': ['*'], 'biobank': ['conf/*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'dask>=2022.2.0,<2023.0.0',
 'pandas>=1.4.1,<2.0.0',
 'pyarrow>=7.0.0,<8.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'typer==0.4.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['autoflake>=1.4,<2.0',
          'black>=21.5b2,<22.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'isort>=5.8.0,<6.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['biobank = biobank.cli:commands']}

setup_kwargs = {
    'name': 'biobank-tools',
    'version': '0.1.2',
    'description': 'Biobank Tools.',
    'long_description': "# Biobank Tools\n\n\n[![pypi](https://img.shields.io/pypi/v/biobank-tools.svg)](https://pypi.org/project/biobank-tools/)\n[![python](https://img.shields.io/pypi/pyversions/biobank-tools.svg)](https://pypi.org/project/biobank-tools/)\n[![Build Status](https://github.com/altaf-ali/biobank-tools/actions/workflows/dev.yml/badge.svg)](https://github.com/altaf-ali/biobank-tools/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/altaf-ali/biobank-tools/branch/main/graphs/badge.svg)](https://codecov.io/github/altaf-ali/biobank-tools)\n\n* Documentation: <https://altaf-ali.github.io/biobank-tools>\n* GitHub: <https://github.com/altaf-ali/biobank-tools>\n* PyPI: <https://pypi.org/project/biobank-tools/>\n\n\n## Features\n\nThe Biobank Tools package provides simple, fast, and efficient access to UK\nBiobank data. Once you've downloaded and extracted the UK Biobank data to\ncomma or tab separated files, you can use Biobank Tools to convert the data\nto a format that's better suited for searching and filtering than plain text\nfiles. Internally, Biobank Tools convert the data to [Apache Parquet][]\nformat for optimized column-wise access.\n\n## Requirements\n\nBiobank Tools require Python 3.8 or above.\n\n## Credits\n\nThis package was created with [Cookiecutter][] and the [altaf-ali/cookiecutter-pypackage][] project template.\n\n[Apache Parquet]: https://parquet.apache.org/documentation/latest\n[Cookiecutter]: https://cookiecutter.readthedocs.io/en/latest/\n[altaf-ali/cookiecutter-pypackage]: https://altaf-ali.github.io/cookiecutter-pypackage\n",
    'author': 'Altaf Ali',
    'author_email': 'altaf@firecrest.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://altaf-ali.github.io/biobank-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
