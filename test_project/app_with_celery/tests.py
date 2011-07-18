"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class CeleryTest(TestCase):

    def test_settings(self):
        # ok, so this doesn't actually run any tasks, but just checks the setting is in place"""
        from django.conf import settings
        self.assertTrue(settings.CELERY_ALWAYS_EAGER)
