"""Retry handling utilities for AMP."""

import time
import random
from typing import Callable, Optional, Tuple, Type, Any
from functools import wraps
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger("retry")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    exceptions: Tuple[Type[Exception], ...] = (Exception,)


def calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool
) -> float:
    """Calculate delay for next retry with exponential backoff."""
    delay = base_delay * (exponential_base ** (attempt - 1))
    delay = min(delay, max_delay)
    if jitter:
        delay = delay * (1 + random.random() * 0.25)
    return delay


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    delay = calculate_delay(attempt, base_delay, max_delay, exponential_base, jitter)
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class RetryContext:
    """Context manager for retry logic."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempt = 0
        self.last_exception: Optional[Exception] = None

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.attempt >= self.config.max_attempts:
            if self.last_exception:
                raise self.last_exception
            raise StopIteration

        if self.attempt > 0 and self.last_exception:
            delay = calculate_delay(
                self.attempt,
                self.config.base_delay,
                self.config.max_delay,
                self.config.exponential_base,
                self.config.jitter,
            )
            time.sleep(delay)

        self.attempt += 1
        return self.attempt

    def record_failure(self, exception: Exception) -> None:
        self.last_exception = exception

    def success(self) -> None:
        self.attempt = self.config.max_attempts


spotify_retry = retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,))
llm_retry = retry(max_attempts=2, base_delay=2.0, max_delay=10.0, exceptions=(Exception,))
