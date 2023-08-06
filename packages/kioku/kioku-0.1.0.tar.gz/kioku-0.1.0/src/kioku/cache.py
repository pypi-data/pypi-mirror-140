"""Cache."""

import pickle
from typing import Any, Callable, Dict, Optional

cache_type = Dict[str, Any]


class Cache:
    """Cache."""

    cache: cache_type

    def __init__(self, path: str, auto_reload=False) -> None:
        """Initialize object.

        Args:
            path (str): Cache path.
            auto_reload (bool, optional): Auto reload or not.
        """
        self.path = path
        self.auto_reload = auto_reload
        try:
            self.load_file()
        except FileNotFoundError:
            self.cache = {}
            self.write_to_file()

    def load_file(self) -> cache_type:
        """Load cache file.

        Returns:
            cache_type: Cache.
        """
        with open(self.path, 'rb') as f:
            self.cache = pickle.load(f)
        return self.cache

    def write_to_file(self) -> None:
        """Write to cache file."""
        with open(self.path, 'wb') as f:
            pickle.dump(self.cache, f)

    def set(self, key: str, value: Any) -> None:  # noqa: A003
        """Set cache value.

        Args:
            key (str): Key name.
            value (Any): Value.
        """
        if self.auto_reload:
            self.load_file()
        self.cache[key] = value
        self.write_to_file()

    def get(self, key: str) -> Any:
        """Get value.

        Args:
            key (str): Key name.

        Returns:
            Any: Value.
        """
        if self.auto_reload:
            self.load_file()
        return self.cache.get(key)

    def clear(self, key: str) -> None:
        """Clear cache.

        Args:
            key (str): Key name.
        """
        if self.auto_reload:
            self.load_file()
        try:
            del self.cache[key]
            self.write_to_file()
        except KeyError:
            pass

    def use(self, name: Optional[str] = None) -> Callable:  # noqa: CFQ004
        """Use cache with decorator.

        Args:
            name (str, optional): Cache name.

        Returns:
            Callable: Result.
        """

        def inner(func):
            k = name if name else func.__name__

            def wrapper():
                v = self.get(k)
                if v:
                    return v
                self.set(k, func())
                return self.get(k)

            return wrapper

        return inner
