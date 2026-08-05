"""Application, error, and request logging configuration."""

import logging
from logging.handlers import RotatingFileHandler

from src.core.settings import AppSettings, Environment

APPLICATION_LOGGER_NAME = "app"
ERROR_LOGGER_NAME = "app.error"
REQUEST_LOGGER_NAME = "app.request"


def get_application_logger() -> logging.Logger:
    return logging.getLogger(APPLICATION_LOGGER_NAME)


def get_error_logger() -> logging.Logger:
    return logging.getLogger(ERROR_LOGGER_NAME)


def get_request_logger() -> logging.Logger:
    return logging.getLogger(REQUEST_LOGGER_NAME)


def _configure_logger(
    logger: logging.Logger,
    level: int,
    handlers: list[logging.Handler],
) -> None:
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False
    for handler in handlers:
        logger.addHandler(handler)


def _stream_handler(formatter: logging.Formatter) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def _file_handler(
    filename: str,
    formatter: logging.Formatter,
    log_directory: str,
) -> logging.Handler:
    handler = RotatingFileHandler(
        filename=f"{log_directory}/{filename}",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    return handler


def configure_logging(settings: AppSettings) -> None:
    """Configure independent rotating logs for application, errors, and requests."""

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    log_directory = settings.log_directory
    log_directory.mkdir(parents=True, exist_ok=True)

    application_handlers = [_stream_handler(formatter)]
    error_handlers = [_stream_handler(formatter)]
    request_handlers = [_stream_handler(formatter)]

    if settings.environment is not Environment.TESTING:
        application_handlers.append(
            _file_handler("application.log", formatter, str(log_directory))
        )
        error_handlers.append(_file_handler("errors.log", formatter, str(log_directory)))
        request_handlers.append(
            _file_handler("requests.log", formatter, str(log_directory))
        )

    _configure_logger(get_application_logger(), level, application_handlers)
    _configure_logger(get_error_logger(), logging.ERROR, error_handlers)
    _configure_logger(get_request_logger(), logging.INFO, request_handlers)
