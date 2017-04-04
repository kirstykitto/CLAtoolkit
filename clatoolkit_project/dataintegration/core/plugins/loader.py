"""
Functions get_module and load are by ojii from:
https://github.com/ojii/django-load.
"""

try:
    from importlib import import_module
except ImportError:
    # Python 2.6 fallback
    try:
        from django.utils.importlib import import_module
    except Exception as e:
        print e

from django.conf import settings

def get_module(app, modname, verbose, failfast):
    """
    Internal function to load a module from a single app.
    """
    module_name = '%s.%s' % (app, modname)
    try:
        module = import_module(module_name)
    except ImportError as e:
        if failfast:
            raise e
        elif verbose:
            print("Could not load %r from %r: %s" % (modname, app, e))
        return None
    if verbose:
        print("Loaded %r from %r" % (modname, app))
    return module

def load(modname, verbose=False, failfast=False):
    """
    Loads all modules with name 'modname' from all installed apps.
    If verbose is True, debug information will be printed to stdout.
    If failfast is True, import errors will not be surpressed.
    """
    for app in settings.INSTALLED_APPS:
        get_module(app, modname, verbose, failfast)

def load_dataintegration_plugins(pluginfolders):
    #load('cladi_plugin', verbose=True, failfast=True)
    for plugin in pluginfolders:
        get_module('dataintegration.plugins.' + plugin, 'cladi_plugin', verbose=True, failfast=False)
