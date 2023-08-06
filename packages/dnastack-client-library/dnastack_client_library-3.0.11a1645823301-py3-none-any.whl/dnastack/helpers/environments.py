import os

from typing import Any, Callable, Optional

__boolean_flag = lambda v: str(v or '').lower() in ['1', 'true']


def env(key: str, default: Any = None, required: bool = False, transform: Optional[Callable] = None) -> Any:
    if key not in os.environ and required:
        raise RuntimeError(f'Missing environment variable: {key}')

    value = os.getenv(key)

    if value is None:
        return default or value
    else:
        return transform(value) if transform else value


def flag(key: str) -> bool:
    return env(key, default=False, transform=__boolean_flag)
