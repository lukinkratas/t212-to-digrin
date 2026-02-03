from logging.config import dictConfig


def configure_logging() -> None:
    """Configure logging."""
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                "format": ("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"),
            },
            "detailed": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                "format": (
                    "%(asctime)s|"
                    "%(levelname)-8s|"
                    "%(name)-20s|"
                    "%(filename)-8s:%(lineno)-3d|"
                    "%(funcName)s: "
                    "%(message)s"
                ),
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "t212_to_digrin": {
                "handlers": ["stdout"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
