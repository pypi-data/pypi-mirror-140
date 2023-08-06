# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gcapi']

package_data = \
{'': ['*'], 'gcapi': ['schemas/*']}

install_requires = \
['Click>=6.0', 'httpx>=0.20.0,<0.21.0', 'jsonschema[format_nongpl]>=3.0']

entry_points = \
{'console_scripts': ['gcapi = gcapi.cli:main']}

setup_kwargs = {
    'name': 'gcapi',
    'version': '0.6.0',
    'description': 'Python client for the grand-challenge.org REST API',
    'long_description': '# Grand Challenge API Client\n\n[![CI](https://github.com/DIAGNijmegen/rse-gcapi/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/DIAGNijmegen/rse-gcapi/actions/workflows/ci.yml?query=branch%3Amaster)\n[![PyPI](https://img.shields.io/pypi/v/gcapi)](https://pypi.org/project/gcapi/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gcapi)](https://pypi.org/project/gcapi/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nPython client for the grand-challenge.org REST API\n\n  - Free software: Apache Software License 2.0\n\n## Features\n\nThis client library is a handy way to interact with the REST API for\ngrand-challenge.org from python, and provides some convenience methods.\nDocumentation and examples can be found on [Grand\nChallenge](https://grand-challenge.org/documentation/grand-challenge-api/).\n',
    'author': 'James Meakin',
    'author_email': 'gcapi@jmsmkn.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DIAGNijmegen/rse-gcapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
