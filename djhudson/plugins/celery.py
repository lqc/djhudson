from __future__ import absolute_import
"""
    Plugin to handle django-celery:  .. _django-celery: http://pypi.python.org/pypi/django-celery
"""
from djhudson.plugins import register, DisablePlugin



@register
class CeleryPlugin(object):

    def __init__(self):
        try:
            import djcelery
        except ImportError as e:
            raise DisablePlugin("No celery module: %r" % e)

    def configure(self, settings, options):
        self.celery_installed = 'djcelery' in settings.INSTALLED_APPS
        self.force_eager = options["djcelery_force_eager"]

    def before_suite_run(self, *args, **kwargs):
        from django.conf import settings
        if self.force_eager:
            settings.CELERY_ALWAYS_EAGER = True

    def add_options(self, group):
        group.add_option("--celery-noforce-eager",
                dest="djcelery_force_eager",
                action="store_false", default=True,
                help="Don't force switching celery into EAGER mode.")
