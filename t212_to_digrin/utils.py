from collections.abc import Callable
from functools import wraps
from typing import Any

from functools import wraps

from io import BytesIO, StringIO
from typing import Any

import pandas as pd


def decode_to_df(encoded_df: bytes, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(StringIO(encoded_df.decode('utf-8')), **kwargs)


def encode_df(decoded_df: pd.DataFrame, **kwargs: Any) -> bytes:
    index = kwargs.pop('index', False)
    bytes = BytesIO()
    decoded_df.to_csv(bytes, index=index, **kwargs)
    bytes.seek(0)
    return bytes.getvalue()

def get_func_name(
    func: Callable[..., Any], args: tuple[Any, ...]
) -> str:
    """Helper function for function name logging.

    Args:
        func: python function
        args: arguments to the function

    Returns: function name
    """
    # check if first argument is class instance (self)
    if args and hasattr(args[0], func.__name__):
        func_name = f'{args[0].__class__.__name__}.{func.__name__}'
        return func_name

    return func.__name__


def log_func(log_func: Callable[..., Any] = print) -> Callable[..., Any]:
    """Decorator factory that accepts a logging function."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator, that wraps the function."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = get_func_name(func, args)

            log_func(f'{func_name}() was called.')
            result = func(*args, **kwargs)
            log_func(f'{func_name} finished successfully.')

            return result

        return wrapper

    return decorator
