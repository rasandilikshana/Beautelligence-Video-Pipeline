"""
Beautelligence Video Pipeline - Rate Limiter

Token bucket rate limiter for API calls.
"""

import asyncio
import time
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """
    Token bucket rate limiter for controlling API call rates.

    Usage:
        limiter = RateLimiter(calls_per_minute=60)
        await limiter.acquire()  # Blocks if rate limit would be exceeded
        await call_api()
    """

    calls_per_minute: int = 60
    _calls: list[float] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @property
    def window_seconds(self) -> float:
        """Time window for rate limiting."""
        return 60.0

    async def acquire(self) -> None:
        """
        Acquire permission to make an API call.
        Blocks if the rate limit would be exceeded.
        """
        async with self._lock:
            now = time.time()

            # Remove calls outside the time window
            self._calls = [t for t in self._calls if now - t < self.window_seconds]

            # Check if we're at the limit
            if len(self._calls) >= self.calls_per_minute:
                # Calculate sleep time
                oldest_call = self._calls[0]
                sleep_time = self.window_seconds - (now - oldest_call) + 0.1
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Clean up again after sleeping
                    now = time.time()
                    self._calls = [t for t in self._calls if now - t < self.window_seconds]

            # Record this call
            self._calls.append(time.time())

    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current window."""
        now = time.time()
        recent_calls = [t for t in self._calls if now - t < self.window_seconds]
        return max(0, self.calls_per_minute - len(recent_calls))

    def is_rate_limited(self) -> bool:
        """Check if currently rate limited."""
        return self.get_remaining_calls() == 0

    def reset(self) -> None:
        """Reset the rate limiter."""
        self._calls = []


# Global rate limiters for different services
gemini_limiter = RateLimiter(calls_per_minute=60)
veo_limiter = RateLimiter(calls_per_minute=10)
