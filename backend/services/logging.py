import logging
import colorlog
import inspect
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from config.settings import get_settings

settings = get_settings()


class Logger:
    """Log service with colored output, file logging, and line numbers."""

    _instances: Dict[str, 'Logger'] = {}

    def __new__(cls, fn: str, debug: Optional[bool] = None) -> 'Logger':
        if fn not in cls._instances:
            cls._instances[fn] = super(Logger, cls).__new__(cls)
            cls._instances[fn]._initialized = False
        return cls._instances[fn]

    def __init__(self, fn: str, debug: Optional[bool] = None) -> None:
        if self._initialized:
            return
        self._initialized = True

        self.logger = logging.getLogger(fn)

        # Determine log level
        log_level = logging.DEBUG if (debug if debug is not None else settings.debug) else logging.INFO
        self.logger.setLevel(log_level)

        # Clear existing handlers to avoid duplication
        self.logger.handlers.clear()

        # Console handler with colors
        stream_handler = logging.StreamHandler()
        color_formatter = colorlog.ColoredFormatter(
            fmt=(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - "
                "[%(filename)s:%(lineno)d] - %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        stream_handler.setFormatter(color_formatter)

        # Simple file handler
        file_handler = logging.FileHandler('app.log')
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        # Attach handlers
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    def set_level(self, level: int) -> None:
        """Set the log level dynamically."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(logging.DEBUG, msg, *args, **kwargs, stacklevel=3)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(logging.INFO, msg, *args, **kwargs, stacklevel=3)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(logging.WARNING, msg, *args, **kwargs, stacklevel=3)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(logging.ERROR, msg, *args, **kwargs, stacklevel=3)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.log(logging.CRITICAL, msg, *args, **kwargs, stacklevel=3)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.exception(msg, *args, **kwargs, stacklevel=3)


def init_logger(debug: Optional[bool] = None) -> Logger:
    """
    Initialize a Logger instance for the calling module.

    Args:
        debug (bool, optional): Override debug mode. Defaults to None.

    Returns:
        Logger: An instance of the Logger class.
    """
    # Get the calling module's name
    frame = inspect.currentframe().f_back
    module_name = inspect.getmodule(frame).__name__

    # Initialize and return the logger
    return Logger(module_name, debug=debug)
