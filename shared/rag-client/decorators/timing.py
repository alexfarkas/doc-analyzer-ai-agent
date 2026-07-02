import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def time_logging_async(func):
    """Декоратор, логирующий время выполнения функции"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger.info(f"'{func.__name__}' is starting...")
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        logger.info(f"'{func.__name__}' is completed in {elapsed:.4f} seconds")
        return result

    return wrapper


def tool_time_logging_async(func):
    """Декоратор, логирующий время выполнения инструмента модели"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger.info(f"Tool '{func.__name__}' is starting...")
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        logger.info(f"Tool '{func.__name__}' is completed in {elapsed:.4f} seconds")
        return result

    return wrapper
