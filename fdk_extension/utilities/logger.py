"""Logger utility."""
__credit__ = "https://docs.python.org/3/howto/logging-cookbook.html#" \
             "adding-contextual-information-to-your-logging-output"

import structlog
from structlog import contextvars
from structlog.stdlib import BoundLogger


def get_logger(*args, **kwargs) -> BoundLogger:
    """Create structlog logger for logging."""

    renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=structlog.threadlocal.wrap_dict(dict),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(**kwargs)


def safe_stringify(obj: object, cache: list=[]) -> dict:
    if hasattr(obj, "__dict__"):
        cache.append(obj)
        temp: dict = obj.__dict__.copy()
        for key, value in temp.items():
            if hasattr(value, "__dict__"):
                if value not in cache:
                    temp[key] = safe_stringify(value, cache)
                else:
                    temp[key] = ""
        return temp
    return obj