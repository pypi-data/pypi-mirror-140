# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cic_utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cic-utils',
    'version': '0.2.5',
    'description': '',
    'long_description': '# CIC-Utils\n[![Status](https://ci.grassecon.net/api/badges/grassrootseconomics/cic-utils/status.svg?ref=refs/heads/main)](https://ci.grassecon.net/grassrootseconomics/cic-utils)\n\n## Development\n### Requirements\n - [poetry](https://python-poetry.org/docs/#installation) \n - `poetry install`\n\n### Testing\n```\npoetry run pytest\n```\n### Publishing\n```\n```',
    'author': 'William Luke',
    'author_email': 'williamluke4@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.grassecon.net/grassrootseconomics/cic-utils',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
