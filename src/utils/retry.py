"""
Beautelligence Video Pipeline - Retry Utilities

Provides retry decorators with exponential backoff for API calls.
"""

import asyncio
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, TypeVar

from config.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_delay: float = 30.0  # seconds
    max_delay: float = 120.0  # seconds
    exponential_base: float = 2.0
    retryable_exceptions: tuple = (Exception,)


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt with exponential backoff."""
    delay = config.initial_delay * (config.exponential_base ** attempt)
    return min(delay, config.max_delay)


def retry_async(
    config: RetryConfig | None = None,
    max_attempts: int | None = None,
    initial_delay: float | None = None,
    retryable_exceptions: tuple | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for async functions with retry logic and exponential backoff.

    Usage:
        @retry_async(max_attempts=3, initial_delay=30)
        async def call_api():
            ...
    """
    if config is None:
        config = RetryConfig()

    # Override config with explicit parameters
    if max_attempts is not None:
        config.max_attempts = max_attempts
    if initial_delay is not None:
        config.initial_delay = initial_delay
    if retryable_exceptions is not None:
        config.retryable_exceptions = retryable_exceptions

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            "retry_attempt",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_attempts=config.max_attempts,
                            delay=delay,
                            error=str(e),
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "retry_exhausted",
                            function=func.__name__,
                            attempts=config.max_attempts,
                            error=str(e),
                        )

            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry state")

        return wrapper

    return decorator


class RetryableError(Exception):
    """Base exception for errors that should trigger retry."""

    pass


class RateLimitError(RetryableError):
    """Exception for rate limit errors."""

    pass


class APIError(RetryableError):
    """Exception for transient API errors."""

    pass
