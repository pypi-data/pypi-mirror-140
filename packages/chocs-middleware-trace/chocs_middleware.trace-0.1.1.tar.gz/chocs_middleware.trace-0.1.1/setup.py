# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chocs_middleware', 'chocs_middleware.trace']

package_data = \
{'': ['*']}

install_requires = \
['chocs>=1.5.3,<2.0.0', 'gid>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'chocs-middleware.trace',
    'version': '0.1.1',
    'description': 'Http tracing middleware for chocs library.',
    'long_description': '# Chocs-Trace <br> [![PyPI version](https://badge.fury.io/py/chocs-middleware.trace.svg)](https://pypi.org/project/chocs-middleware.trace/) [![CI](https://github.com/kodemore/chocs-trace/actions/workflows/main.yaml/badge.svg)](https://github.com/kodemore/chocs-trace/actions/workflows/main.yaml) [![Release](https://github.com/kodemore/chocs-trace/actions/workflows/release.yml/badge.svg)](https://github.com/kodemore/chocs-trace/actions/workflows/release.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\nHttp tracing middleware for chocs library. \n\n\n# Installation\n\n### Poetry:\n```bash\npoetry add chocs-middleware.trace\n```\n\n### Pip:\n```bash\npip install chocs-middleware.trace\n```\n',
    'author': 'Dawid Kraczkowski',
    'author_email': 'dawid.kraczkowski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kodemore/chocs-trace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
