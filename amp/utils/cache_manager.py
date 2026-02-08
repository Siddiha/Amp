"""Cache management utilities for AMP."""

import time
import hashlib
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass, field
from functools import wraps
from threading import Lock

from .logger import get_logger

logger = get_logger("cache")


@dataclass
class CacheEntry:
    """Single cache entry with expiration."""
    value: Any
    expires_at: float
    hits: int = 0


class CacheManager:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if time.time() > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            entry.hits += 1
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            expires_at = time.time() + (ttl or self._default_ttl)
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def clear_expired(self) -> int:
        with self._lock:
            now = time.time()
            expired = [k for k, v in self._cache.items() if now > v.expires_at]
            for key in expired:
                del self._cache[key]
            return len(expired)

    def _evict_oldest(self) -> None:
        entries = sorted(self._cache.items(), key=lambda x: x[1].expires_at)
        evict_count = max(1, len(entries) // 10)
        for key, _ in entries[:evict_count]:
            del self._cache[key]

    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
            }


_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def cache(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            cache_instance = get_cache()
            result = cache_instance.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
