from django.utils.datastructures import SortedDict
import importlib


__all__ = [
    'get_plugins',
    'register_plugin',
    'trigger_plugin_signal',
    'DisablePlugin'
]


DEFAULT_PLUGINS = (
    "djhudson.plugins.coverage.CoveragePlugin",
    "djhudson.plugins.celery.CeleryPlugin",
    "djhudson.plugins.south.SouthPlugin",
)

__plugins = None


class DisablePlugin(Exception):
    pass


def get_plugins():
    global __plugins
    if __plugins is not None:
        return __plugins
    # Initialize plugins
    from django.conf import settings
    plugin_classes = getattr(settings, "DJHUDSON_PLUGINS", DEFAULT_PLUGINS)
    __plugins = []
    for path in plugin_classes:
        modpath, class_name = path.rsplit(".", 1)
        mod = importlib.import_module(modpath, package=None)
        try:
            __plugins.append(getattr(mod, class_name)())
        except DisablePlugin:
            pass
    return __plugins


def register(plugin):
    # Deprecated - does nothing
    return plugin


def trigger_plugin_signal(signal, *args, **kwargs):
    global __plugins
    for plugin in __plugins:
        callback = getattr(plugin, signal, None)
        if callback is not None:
            callback(*args, **kwargs)
