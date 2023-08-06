# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kioku']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'kioku',
    'version': '0.1.0',
    'description': 'Python package project template.',
    'long_description': "# kioku\n\nSimple Cache Library for Python.\n\n## Usage\n\n### Quick Start\n\n```python\nimport time\n\nfrom kioku import Cache\n\ncache = Cache('./cache.pkl')\n\n@cache.use()\ndef calc():\n   time.sleep(3)\n   return 42\n\n# It takes 3 sec...\nprint(calc())\n# => 42\n\n# Without to run calc() by using cache.\nprint(calc())\n# => 42\n\n# Cache is saved as dict.\n# And key is function name.\nprint(cache.get('calc'))\n# => 42\n```\n\n### Basic\n\n```py\n# Set manually\ncache.set('key', 123)\nprint(cache.get('key'))\n# => 123\n\n# Clear\ncache.clear('key')\nprint(cache.get('key'))\n# => None\n```\n\n### Auto Reloading Cache File\n\n```py\ncache = Cache('cache.pkl', auto_reload=True)\n```\n\n\n## Development\n\n* Requirements: poetry, pyenv\n\n```sh\n# Setup\npoetry install\n\n# Lint & Test\nmkdir -p report\npoetry run flake8 --format=html --htmldir=report/flake-report .\nmypy src/ tests/ --html-report report/mypy\npoetry run pytest \\\n   --html=report/pytest/index.html\\\n   --cov-report html:report/coverage\n\n# Build and publish\npoetry build\npoetry publish\n```\n",
    'author': 'Takeru Saito',
    'author_email': 'takelushi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/takelushi/kioku',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
