#!/usr/bin/env python3

### IMPORTS ###
from .plugin import Plugin

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ExampleLoggingPlugin(Plugin):
    required_services = ["logging"]
    def __init__(self, services):
        super().__init__(services)
        self.logger.debug("Inputs - services: %s", services)

    def setup(self):
        # This method should do whatever is needed to initialize the plugin's operation.
        self.logger.debug("setup method")

    def tick(self):
        # FIXME: Pick a better name for this
        # This method should do some small piece of work for the plugin.
        self.logger.debug("tick method")

    def teardown(self):
        # This method should do whatever is needed to un-setup the plugin, stopping operation.
        self.logger.debug("teardown method")