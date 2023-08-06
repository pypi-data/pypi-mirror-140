# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pel',
 'pel._vendor',
 'pel._vendor.dateutil',
 'pel._vendor.dateutil.parser',
 'pel._vendor.dateutil.tz',
 'pel._vendor.dateutil.zoneinfo',
 'pel._vendor.graphlib']

package_data = \
{'': ['*'],
 'pel._vendor': ['graphlib_backport-1.0.3.dist-info/*',
                 'python_dateutil-2.8.2.dist-info/*']}

entry_points = \
{'console_scripts': ['pel = pel.console:run']}

setup_kwargs = {
    'name': 'pel',
    'version': '0.0.1',
    'description': 'The most elegant build system.',
    'long_description': '# Pel is the most elegant build system\n## Introduction\n\nPel is an easy-to-use build system/task runner written in Python. It is designed to be more advanced than task runners like [Make](https://www.gnu.org/software/make/) or [Invoke](https://www.pyinvoke.org/), but much simpler than complex build systems like [CMake](https://cmake.org/) or [Bazel](https://bazel.build/).\n\n## Installation\n\n### Installation from pip\n\n```\npip3 install --user pel\n```\n\nIt is safe to install Pel as a global Python package. **Installing Pel will never modify any other Python packages on your computer.**\n\n## Development status\n\nPel is still in the early stages of development. It is not currently ready for production use.\n\n## Features\n\n### Cross-platform support\n\nPel is written in pure Python, and is intended to work on any operating system supported by Python, such as:\n* Linux\n* Windows\n* macOS\n* FreeBSD\n\n## Why we made Pel\n\nMost build systems are either **too simple** or **too complex**.\n\n * A **simple** build system, like [Make](https://www.gnu.org/software/make/) or [Invoke](https://www.pyinvoke.org/) makes it easy to run arbitrary shell commands, but makes it hard to add non-trivial dependency management and build caching\n * A **complex** build system, like [CMake](https://cmake.org/) or [Bazel](https://bazel.build/), offers sophisticated dependency management and build caching, but only for predefined types of build targets. These build systems are excellent choices for building a large C++ monorepo, but can be unwieldy to integrate with arbitrary commands and obscure build tools.\n\nPel is designed to be the happy medium between simple and complex.\n',
    'author': 'Neocrym Records Inc.',
    'author_email': 'engineering@neocrym.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/neocrym/pel',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
