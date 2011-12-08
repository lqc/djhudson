from django.test import TestCase


class ExcludedTest(TestCase):

    def test_excluded(self):
        self.fail("This test should never run.")
