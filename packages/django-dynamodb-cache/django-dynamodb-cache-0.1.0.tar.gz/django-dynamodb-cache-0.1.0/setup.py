# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_dynamodb_cache',
 'django_dynamodb_cache.compact',
 'django_dynamodb_cache.compact.django',
 'django_dynamodb_cache.compact.django.management.command',
 'django_dynamodb_cache.encode']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2,<4.0', 'boto3>=1.21.9,<2.0.0', 'botocore>=1.24.9,<2.0.0']

setup_kwargs = {
    'name': 'django-dynamodb-cache',
    'version': '0.1.0',
    'description': '',
    'long_description': '# django-dynamodb-cache [WIP]\n\n<p align="center">\n<a href="https://github.com/xncbf/django-dynamodb-cache/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/xncbf/django-dynamodb-cache/workflows/Tests/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/xncbf/django-dynamodb-cache" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/xncbf/django-dynamodb-cache?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/django-dynamodb-cache" target="_blank">\n    <img src="https://img.shields.io/pypi/v/django-dynamodb-cache?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/django-dynamodb-cache" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/django-dynamodb-cache.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n- [django-dynamodb-cache [WIP]](#django-dynamodb-cache-wip)\n  - [Introduce](#introduce)\n  - [Installation](#installation)\n  - [Dependency](#dependency)\n  - [Example](#example)\n  - [Contribution](#contribution)\n\n## Introduce\n\ndjango cache backend for DynamoDB\n\n## Installation\n\n```sh\npip install django-dynamodb-cache\n```\n\n## Dependency\n\n- python == ^3.8\n- django == ^3.2\n\n## Example\n\n\n## Contribution\n',
    'author': 'xncbf',
    'author_email': 'xncbf12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xncbf/django-dynamodb-cache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
