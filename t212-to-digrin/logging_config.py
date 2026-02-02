import logging
from logging.config import dictConfig


def configure_logging() -> None:
    """Configure logging."""

    cfg = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%dT%H:%M:%SZ',
                'format': (
                    '%(asctime)s | '
                    '%(levelname)-8s | '
                    '%(name)s | '
                    '[%(correlation_id)s] %(message)s'
                ),
            },
            'detailed': {
                'class': 'logging.Formatter',
                'datefmt': '%Y-%m-%dT%H:%M:%SZ',
                'format': (
                    '%(asctime)s | '
                    '%(levelname)-8s | '
                    '%(name)s | '
                    '%(filename)s:%(lineno)d | '
                    '%(funcName)s | '
                    '[%(correlation_id)s] %(message)s'
                ),
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'DEBUG',
                'filters': ['correlation_id', 'mask_email'],
            },
        },
        'loggers': {
            'api': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
    dictConfig(cfg)
