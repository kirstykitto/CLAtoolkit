try:
    from importlib import import_module
except ImportError:
    # Python 2.6 fallback
    try:
        from django.utils.importlib import import_module
    except ImportError as e:
        print e

from dataintegration.core.plugins.base import DIPluginDashboardMixin, DIAuthomaticPluginMixin

_cache = {}
_includeindashboardwidgets = {}
_includeverbsindashboardwidgets = set()
_includeplatformsindashboardwidgets = set()
_includeauthomaticplugins = set()

def register(PluginClass):
    """
    Register a plugin class. This function will call back your plugin's
    constructor.
    """
    if PluginClass in list(_cache.keys()):
        raise Exception("Plugin class already registered")
    plugin = PluginClass()
    platform = getattr(PluginClass, 'platform', None)
    _cache[platform] = plugin

    if issubclass(PluginClass, DIPluginDashboardMixin):
        _includeindashboardwidgets[PluginClass] = plugin
        if getattr(PluginClass, 'xapi_objects_to_includein_platformactivitywidget', None):
            _includeplatformsindashboardwidgets.update(PluginClass.xapi_objects_to_includein_platformactivitywidget)
        if getattr(PluginClass, 'xapi_verbs_to_includein_verbactivitywidget', None):
            _includeverbsindashboardwidgets.update(PluginClass.xapi_verbs_to_includein_verbactivitywidget)

    if issubclass(PluginClass, DIAuthomaticPluginMixin):
        _includeauthomaticplugins.add(PluginClass.platform)

def get_plugins():
    """Get loaded plugins - do not call before all plugins are loaded."""
    return _cache

def get_includeindashboardwidgets():
    """Get all extension classes from plugins that require verbs and objects included in temporal dashboard"""
    return _includeindashboardwidgets

def get_includeindashboardwidgets_verbs():
    """Get all extension classes from plugins that require verbs and objects included in temporal dashboard"""
    return _includeverbsindashboardwidgets

def get_includeindashboardwidgets_platforms():
    """Get all extension classes from plugins that require verbs and objects included in temporal dashboard"""
    return _includeplatformsindashboardwidgets

def get_includeauthomaticplugins_platforms():
    """Get all extension classes from plugins that require verbs and objects included in temporal dashboard"""
    return _includeauthomaticplugins
