import logging
import logging.handlers

__all__ = [
    'Logger',
]

import sys

from typing import Dict

_trace = getattr(logging, 'TRACE', 9)


# noinspection PyProtectedMember
class Logger:
    def __init__(self, category: str, logger=None, q=None) -> None:
        self.message_start = f'{category[:12] if len(category) > 12 else category}: '
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.handlers.QueueHandler(q)
            ch.setLevel(_trace)
            self.logger.addHandler(ch)
            self.logger.setLevel(_trace)

    @staticmethod
    def _check_exc_info(exc_info: bool, kwargs: Dict) -> Dict:
        if exc_info and sys.exc_info() != (None, None, None):
            kwargs['exc_info'] = True
        else:
            kwargs['exc_info'] = False
        return kwargs

    def log(self, level: int, *message, **kwargs) -> None:
        if self.logger.isEnabledFor(level):
            self.logger._log(
                level, self.message_start + " ".join(list(map(str, message))), (), **kwargs,
            )

    def trace(self, *message, **kwargs) -> None:
        if self.logger.isEnabledFor(_trace):
            self.logger._log(
                _trace, self.message_start + " ".join(list(map(str, message))), (), **kwargs,
            )

    def debug(self, *message, **kwargs) -> None:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger._log(
                logging.DEBUG, self.message_start + " ".join(list(map(str, message))), (), **kwargs,
            )

    def info(self, *message, **kwargs) -> None:
        if self.logger.isEnabledFor(logging.INFO):
            self.logger._log(
                logging.INFO, self.message_start + " ".join(list(map(str, message))), (), **kwargs,
            )

    def warning(self, *message, exc_info=True, **kwargs) -> None:
        if self.logger.isEnabledFor(logging.WARNING):
            self.logger._log(
                logging.WARNING, self.message_start + " ".join(list(map(str, message))),
                (), **self._check_exc_info(exc_info, kwargs),
            )

    warn = warning

    def exception(self, *message, exc_info=True, **kwargs) -> None:
        if self.logger.isEnabledFor(logging.ERROR):
            self.logger._log(
                logging.ERROR, self.message_start + " ".join(list(map(str, message))),
                (), **self._check_exc_info(exc_info, kwargs),
            )

    error = exception

    def critical(self, *message, exc_info=True, **kwargs) -> None:
        if self.logger.isEnabledFor(logging.CRITICAL):
            self.logger._log(
                logging.CRITICAL, self.message_start + " ".join(list(map(str, message))),
                (), **self._check_exc_info(exc_info, kwargs),
            )

    def spawn(self, category: str) -> 'Logger':
        if len(category) > 12:
            category = category[:12]
        return Logger(category, logger=self.logger)
