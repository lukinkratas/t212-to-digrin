from logging.config import dictConfig


def configure_logging() -> None:
    """Configure logging."""
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                "format": "%(asctime)s | %(levelname)-8s | %(name)-19s | %(message)s",
            },
        },
        "handlers": {
            "stream_handler": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "t212_to_digrin": {
                "handlers": ["stream_handler"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
