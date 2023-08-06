# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pywikibot_extensions']

package_data = \
{'': ['*']}

install_requires = \
['pywikibot>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'pywikibot-extensions',
    'version': '22.3.1',
    'description': 'Extends the Pywikibot library',
    'long_description': '[![Latest PyPI release](https://img.shields.io/pypi/v/pywikibot-extensions?logo=pypi)](https://pypi.org/project/pywikibot-extensions) ![Latest GitHub release](https://img.shields.io/github/v/release/JJMC89/pywikibot-extensions?logo=github) ![Latest tag](https://img.shields.io/github/v/tag/JJMC89/pywikibot-extensions?logo=git)\n\n![License](https://img.shields.io/pypi/l/pywikibot-extensions?color=blue) ![Python versions](https://img.shields.io/pypi/pyversions/pywikibot-extensions?logo=python)\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/JJMC89/pywikibot-extensions/main.svg)](https://results.pre-commit.ci/latest/github/JJMC89/pywikibot-extensions/main) [![CI](https://github.com/JJMC89/pywikibot-extensions/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/JJMC89/pywikibot-extensions/actions?query=workflow%3ACI+branch%3Amain)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# pywikibot-extensions\nThe pywikibot-extensions library extends the [Pywikibot](https://pywikibot.org) library.\n\n## Installation\n`pip install pywikibot-extensions`\n',
    'author': 'JJMC89',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JJMC89/pywikibot-extensions',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
