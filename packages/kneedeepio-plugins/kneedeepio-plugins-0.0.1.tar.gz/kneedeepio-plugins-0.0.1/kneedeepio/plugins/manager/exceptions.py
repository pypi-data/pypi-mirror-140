#!/usr/bin/env python3

### IMPORTS ###

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class KneeDeepIOPluginsManagerException(Exception):
    pass

class ServiceAlreadyRegistered(KneeDeepIOPluginsManagerException):
    pass

class ServiceNotRegistered(KneeDeepIOPluginsManagerException):
    pass

class PluginAlreadyLoadedException(KneeDeepIOPluginsManagerException):
    pass

class PluginNotLoadedException(KneeDeepIOPluginsManagerException):
    pass
