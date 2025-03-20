import sys
from typing import NoReturn


def raise_error(err: str, code: int = 1) -> NoReturn:
    sys.exit(err)
