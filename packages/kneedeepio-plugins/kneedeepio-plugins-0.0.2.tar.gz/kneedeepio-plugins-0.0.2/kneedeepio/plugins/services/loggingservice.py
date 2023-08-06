#!/usr/bin/env python3

### IMPORTS ###
import abc
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class LoggingService(metaclass = abc.ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abc.abstractmethod
    def debug(self, msg, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def info(self, msg, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def warning(self, msg, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def error(self, msg, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def critical(self, msg, *args, **kwargs):
        raise NotImplementedError

class InProcessLoggingService(LoggingService):
    def __init__(self):
        super().__init__()
        self.logger.debug("Inputs - None")
        self._data = {}

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
