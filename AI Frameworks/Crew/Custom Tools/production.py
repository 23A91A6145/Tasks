import asyncio
import functools
import random
import threading
import time
from collections import OrderedDict


class RateLimiter:
    """Token bucket rate limiter — controls calls per second.

    Usage:
        limiter = RateLimiter(calls_per_second=5)

        # As decorator
        @limiter
        def my_func(): ...

        # As context manager
        with limiter:
            my_func()

        # Direct
        limiter.acquire()
    """
    def __init__(self, calls_per_second: float = 10):
        if calls_per_second <= 0:
            raise ValueError("calls_per_second must be positive")
        self.rate = calls_per_second
        self.max_tokens = calls_per_second
        self.tokens = calls_per_second
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def acquire(self, blocking: bool = True) -> bool:
        """Acquire a token. If blocking, wait until one is available."""
        while True:
            with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            if not blocking:
                return False
            time.sleep(1 / self.rate)

    async def async_acquire(self) -> bool:
        """Async version of acquire."""
        while True:
            with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            await asyncio.sleep(1 / self.rate)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        pass

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)
        return wrapper


class ToolCache:
    """LRU cache with TTL for tool results.

    Usage:
        cache = ToolCache(maxsize=128, ttl=300)

        @cache
        def expensive_tool(text): ...

        # Direct
        cache.set("key", value)
        value = cache.get("key")
    """
    def __init__(self, maxsize: int = 128, ttl: float = 300):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache = OrderedDict()
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}
        self._lock = threading.Lock()

    def _is_expired(self, entry) -> bool:
        return time.monotonic() - entry["time"] > self.ttl

    def _evict_expired(self):
        now = time.monotonic()
        while self._cache:
            _key, entry = next(iter(self._cache.items()))
            if now - entry["time"] > self.ttl:
                self._cache.popitem(last=False)
                self._stats["evictions"] += 1
            else:
                break

    def get(self, key: str):
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if self._is_expired(entry):
                    del self._cache[key]
                    self._stats["misses"] += 1
                    return None
                self._cache.move_to_end(key)
                self._stats["hits"] += 1
                return entry["value"]
            self._stats["misses"] += 1
            return None

    def set(self, key: str, value):
        with self._lock:
            self._evict_expired()
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = {"value": value, "time": time.monotonic()}
            self._stats["sets"] += 1
            while len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)
                self._stats["evictions"] += 1

    def stats(self) -> dict:
        with self._lock:
            return {**self._stats, "size": len(self._cache)}

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = self.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            self.set(key, result)
            return result
        return wrapper


def with_retry(max_retries: int = 3, base_delay: float = 1.0,
               backoff: float = 2.0, max_delay: float = 60.0,
               exceptions=None):
    """Decorator that retries on failure with exponential backoff + jitter.

    Args:
        max_retries: Max number of retries before giving up.
        base_delay: Initial delay in seconds.
        backoff: Multiplier for each retry.
        max_delay: Maximum delay cap.
        exceptions: Tuple of exception types to retry on (default: Exception).
    """
    if exceptions is None:
        exceptions = (Exception,)

    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exc = None
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_retries:
                        raise
                    jitter = random.uniform(0, delay * 0.1)
                    time.sleep(min(delay + jitter, max_delay))
                    delay = min(delay * backoff, max_delay)
            raise last_exc

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exc = None
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_retries:
                        raise
                    jitter = random.uniform(0, delay * 0.1)
                    await asyncio.sleep(min(delay + jitter, max_delay))
                    delay = min(delay * backoff, max_delay)
            raise last_exc

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def batch_process(func, inputs: list, max_concurrency: int = 5):
    """Process multiple inputs concurrently with bounded concurrency.

    Args:
        func: Function to apply to each input.
        inputs: List of input dicts (or positional args as tuples).
        max_concurrency: Max concurrent executions.

    Returns:
        List of results in original order.
    """
    results = [None] * len(inputs)
    lock = threading.Lock()
    idx = 0

    def worker():
        nonlocal idx
        while True:
            with lock:
                if idx >= len(inputs):
                    return
                i = i_val = idx
                inp = inputs[i]
                idx += 1
            try:
                if isinstance(inp, dict):
                    result = func(**inp)
                elif isinstance(inp, (tuple, list)):
                    result = func(*inp)
                else:
                    result = func(inp)
                with lock:
                    results[i_val] = result
            except Exception as e:
                with lock:
                    results[i_val] = e

    threads = []
    for _ in range(min(max_concurrency, len(inputs))):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return results


async def async_batch_process(func, inputs: list, max_concurrency: int = 5):
    """Async version of batch_process using asyncio.Semaphore.

    Supports both plain async callables and LangChain tools (uses ainvoke).
    """
    is_langchain_tool = hasattr(func, "ainvoke") and callable(func.ainvoke)
    sem = asyncio.Semaphore(max_concurrency)

    async def worker(inp):
        async with sem:
            if is_langchain_tool:
                return await func.ainvoke(inp)
            if isinstance(inp, dict):
                return await func(**inp)
            elif isinstance(inp, (tuple, list)):
                return await func(*inp)
            return await func(inp)

    tasks = [worker(inp) for inp in inputs]
    return await asyncio.gather(*tasks, return_exceptions=True)
