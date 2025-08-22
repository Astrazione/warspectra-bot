from typing import Dict
from models.user_cache import UserCache


class ChatCache:
    _cache: Dict[int, UserCache] = {}

    def __getitem__(self, key: int) -> 'UserCache':
        return self._cache[key]

    def __setitem__(self, key: int, value: 'UserCache') -> None:
        self._cache[key] = value

    def __delitem__(self, key: int) -> None:
        del self._cache[key]

    def __contains__(self, key: int) -> bool:
        return key in self._cache
    