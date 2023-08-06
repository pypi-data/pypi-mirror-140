# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['patchguard', 'patchguard.app']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.6,<0.7',
 'asyncpg>=0.22,<0.23',
 'fastapi>=0.65,<0.66',
 'psycopg2-binary>=2.8,<3.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'rich>=10.4,<11.0',
 'typer>=0,<1',
 'uvicorn>=0.13,<0.14']

extras_require = \
{'docs': ['sphinx-autodoc-typehints>=1.12,<2.0',
          'sphinx-rtd-theme>=0.5,<0.6',
          'sphinx-click>=3.0,<4.0',
          'Sphinx<4',
          'myst-parser>=0.17.0,<0.18.0']}

entry_points = \
{'console_scripts': ['fact-explorer = patchguard.cli.main:app']}

setup_kwargs = {
    'name': 'patchguard',
    'version': '0.0.1',
    'description': 'A way to view your renovate status across gitlab projects',
    'long_description': '# Patch Guard\n\nWelcome to patch_guard. You can find more extensive documentation over at [readthedocs](https://patchguard.readthedocs.io/en/latest/).\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install patchguard` and get going. The cli is available as `patchguard` and\nyou can run `patchguard --help` to get up to speed on what you can do.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n',
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/friendly-security/patchguard',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
