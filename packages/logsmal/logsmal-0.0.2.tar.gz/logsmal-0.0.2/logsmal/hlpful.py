from typing import Final


class MetaLogger:
    """
    Мета данные логгера
    """
    reset_: Final[str] = "\x1b[0m"
    blue: Final[str] = "\x1b[96m"
    yellow: Final[str] = "\x1b[93m"
    read: Final[str] = "\x1b[91m"
    green: Final[str] = "\x1b[92m"
    #: Серый
    gray: Final[str] = "\x1b[90m"
    #: Неон
    neon: Final[str] = "\x1b[96m"
