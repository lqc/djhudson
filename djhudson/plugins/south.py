from __future__ import absolute_import
"""
    Plugin to handle django-south_ migrations while testing.

    .. _django-south: http://south.aeracode.org/
"""
from djhudson.plugins import register, DisablePlugin



@register
class SouthPlugin(object):

    def __init__(self):
        try:
            import south
        except ImportError as e:
            raise DisablePlugin("No south module: %r" % e)

    def configure(self, settings, options):
        self.south_installed = 'south' in settings.INSTALLED_APPS

    def before_database_setup(self):
        if self.south_installed:
            from south.management.commands import patch_for_test_db_setup
            patch_for_test_db_setup()

    def add_options(self, group):
        pass
