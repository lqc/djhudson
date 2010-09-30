__all__ = [
    'get_plugins',
    'register_plugin',
    'trigger_plugin_signal',
    'DisablePlugin'
]

from django.utils.datastructures import SortedDict

__plugins = SortedDict()

class DisablePlugin(Exception):
    pass

def get_plugins():
    return __plugins.values()

def register(plugin):
    """
        Class decorator for registering plugins.
    """
    global __plugins

    qname = plugin.__module__ + '.' + plugin.__name__
    if qname in __plugins:
        raise ValueError("Test plugin '%s' already registered" % qname)
    try:
        __plugins[qname] = plugin()
    except DisablePlugin, e:
        print "Plugin %s is disabled: %s" % (qname, e.args[0])
    return plugin

def trigger_plugin_signal(signal, *args, **kwargs):
    global __plugins

    for plugin in __plugins.itervalues():
        callback = getattr(plugin, signal, None)
        if callback is not None:
            callback(*args, **kwargs)
