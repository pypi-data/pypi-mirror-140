# kioku

Simple Cache Library for Python.

## Usage

### Quick Start

```python
import time

from kioku import Cache

cache = Cache('./cache.pkl')

@cache.use()
def calc():
   time.sleep(3)
   return 42

# It takes 3 sec...
print(calc())
# => 42

# Without to run calc() by using cache.
print(calc())
# => 42

# Cache is saved as dict.
# And key is function name.
print(cache.get('calc'))
# => 42
```

### Basic

```py
# Set manually
cache.set('key', 123)
print(cache.get('key'))
# => 123

# Clear
cache.clear('key')
print(cache.get('key'))
# => None
```

### Auto Reloading Cache File

```py
cache = Cache('cache.pkl', auto_reload=True)
```


## Development

* Requirements: poetry, pyenv

```sh
# Setup
poetry install

# Lint & Test
mkdir -p report
poetry run flake8 --format=html --htmldir=report/flake-report .
mypy src/ tests/ --html-report report/mypy
poetry run pytest \
   --html=report/pytest/index.html\
   --cov-report html:report/coverage

# Build and publish
poetry build
poetry publish
```
