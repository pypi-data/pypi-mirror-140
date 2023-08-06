#!/usr/bin/env python3

### IMPORTS ###
import abc
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ObjectDatastoreService(metaclass = abc.ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abc.abstractmethod
    def get_value(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def set_value(self, key, value):
        raise NotImplementedError


class InMemoryObjectDatastoreService(ObjectDatastoreService):
    def __init__(self):
        super().__init__()
        self.logger.debug("Inputs - None")
        self._data = {}

    def get_value(self, key):
        self.logger.debug("Getting value for key: %s - %s", key, self._data[key])
        return self._data[key]

    def set_value(self, key, value):
        self.logger.debug("Setting value for key: %s - %s", key, value)
        self._data[key] = value
