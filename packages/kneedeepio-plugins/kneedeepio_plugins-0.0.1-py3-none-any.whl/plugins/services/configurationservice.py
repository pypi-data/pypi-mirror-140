#!/usr/bin/env python3

### IMPORTS ###
import abc
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ConfigurationService(metaclass = abc.ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abc.abstractmethod
    def load_config(self, config):
        raise NotImplementedError

    @abc.abstractmethod
    def get_value(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def set_value(self, key, value):
        raise NotImplementedError

class InMemoryConfigurationService(ConfigurationService):
    def __init__(self):
        super().__init__()
        self.logger.debug("Inputs - None")
        self._data = {}

    def load_config(self, config):
        self.logger.debug("Loading config: %s", config)
        for item_key, item_value in config.items():
            self.set_value(item_key, item_value)

    def get_value(self, key):
        self.logger.debug("Getting value for key: %s - %s", key, self._data[key])
        return self._data[key]

    def set_value(self, key, value):
        self.logger.debug("Setting value for key: %s - %s", key, value)
        self._data[key] = value