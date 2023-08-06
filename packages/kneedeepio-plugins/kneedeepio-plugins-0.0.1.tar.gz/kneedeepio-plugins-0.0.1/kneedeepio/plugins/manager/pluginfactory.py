#!/usr/bin/env python3

### IMPORTS ###
import logging
import importlib

from kneedeepio.plugins.plugin import Plugin

from .exceptions import ServiceAlreadyRegistered
from .exceptions import ServiceNotRegistered
from .exceptions import PluginAlreadyLoadedException
from .exceptions import PluginNotLoadedException

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class PluginFactory:
    def __init__(self, logging_srv):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - logging_srv: %s", logging_srv)

        self._service_registry = {}
        self._plugin_registry = []
        self._load_callbacks = []
        self._unload_callbacks = []

        self.register_service("logging", logging_srv)

    def register_service(self, service_type, service):
        self.logger.debug("Inputs - service_type: %s, service: %s", service_type, service)
        # Check if service type already registered.
        if service_type in self._service_registry:
            raise ServiceAlreadyRegistered("Service of type {} already registered.".format(service_type))
        # Put service in registry
        self._service_registry[service_type] = service

    def load(self, module_name, class_name):
        self.logger.debug("Inputs - module_name: %s, class_name: %s", module_name, class_name)
        # Check if plugin is already loaded
        for loaded_plugin in self._plugin_registry:
            if loaded_plugin["module_name"] == module_name and loaded_plugin["class_name"] == class_name:
                raise PluginAlreadyLoadedException
        # Import the plugin
        tmp_module = importlib.import_module(module_name)
        self.logger.debug("tmp_module: %s", tmp_module)
        # Create an instance of the plugin
        tmp_class = getattr(tmp_module, class_name)
        if not issubclass(tmp_class, Plugin):
            raise TypeError("Plugin does not subclass kneedeepio.plugins.plugin.Plugin")
        self.logger.debug("tmp_class: %s", tmp_class)
        # NOTE: The logging service is always provided as it should always be used.
        tmp_services = {"logging": self._service_registry["logging"]}
        for tmp_service_type in tmp_class.required_services:
            if tmp_service_type in self._service_registry:
                tmp_services[tmp_service_type] = self._service_registry[tmp_service_type]
            else:
                raise ServiceNotRegistered("Service type '{}' not registered.".format(tmp_service_type))
        tmp_instance = tmp_class(tmp_services)
        self.logger.debug("tmp_instance: %s", tmp_instance)
        # Store the instance in the registry list
        self._plugin_registry.append({
            "module_name": module_name,
            "class_name": class_name,
            "instance": tmp_instance
        })
        # Run the plugin instance setup
        tmp_instance.setup()
        # Call the load callbacks
        for cb in self._load_callbacks:
            cb(tmp_instance)

    def unload(self, module_name, class_name):
        self.logger.debug("Inputs - module_name: %s, class_name: %s", module_name, class_name)
        # Check if plugin is already loaded
        tmp_plugin = None
        for loaded_plugin in self._plugin_registry:
            if loaded_plugin["module_name"] == module_name and loaded_plugin["class_name"] == class_name:
                tmp_plugin = loaded_plugin
        if tmp_plugin is None:
            raise PluginNotLoadedException
        # Call the unload callbacks
        for cb in self._unload_callbacks:
            cb(tmp_plugin["instance"])
        # Run the plugin instance teardown
        tmp_plugin["instance"].teardown()
        # Remove the instance from the registry
        self._plugin_registry.remove(tmp_plugin)
        # FIXME: How to un-import the plugin module?
        #        Is the un-import necessary?
        #        Have to check to make sure there aren't any other classes using
        #           the same module.

    def register_load_callback(self, callback_method):
        self.logger.debug("Inputs - callback_method: %s", callback_method)
        # Add the callback method to the list of methods to call back on plugin load.
        # The callback method should take one argument: the instance of the plugin.
        self._load_callbacks.append(callback_method)

    def register_unload_callback(self, callback_method):
        self.logger.debug("Inputs - callback_method: %s", callback_method)
        # Add the callback method to the list of methods to call back on plugin unload.
        # The callback method should take one argument: the instance of the plugin.
        self._unload_callbacks.append(callback_method)

    def tick_plugins(self):
        self.logger.debug("Inputs - None")
        # Call the tick function for each of the plugins.
        # This can be used as a heartbeat for the plugin, or used to perform a
        #    small amount of work.
        for item in self._plugin_registry:
            item["instance"].tick()