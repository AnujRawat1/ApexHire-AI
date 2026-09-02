import logging
import sys
import contextvars
from typing import Optional

request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Injects current request ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "N/A"
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configures application-wide structured logging."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s:%(lineno)d | %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    # Remove existing handlers to avoid duplicates
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)

    # Set quieter levels for noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
