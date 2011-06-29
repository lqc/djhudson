# -*- coding: utf-8
from django.utils import unittest

class MetaTests(unittest.TestCase):
    """
        This test case exists only to see how Hudson displays our reports.
    """

    def test_meta_success(self):
        self.assertTrue(True)

    def test_nonascii_string_failue(self):
        raise Exception("Gąska i Gżegżółka")

    def test_nonascii_string_assert(self):
        self.fail("Gąska i Gżegżółka")

    @unittest.skip("This test is skipped!")
    def test_meta_skipping(self):
        # this test will fail, but it will never be runned
        self.assertEqual(0, 1, "Broken!")

    @unittest.expectedFailure
    def test_meta_expected_failure(self):
        # this will fail, but we expect it
        self.assertEqual(0, 1, "Broken!")

    @unittest.expectedFailure
    def test_meta_unexpected_success(self):
        self.assertEqual(1, 1, "It works after all!")


class BrokenTestCase(unittest.TestCase):

    def setUp(self):
        raise Exception("Unexpected error")

    def test_unreachable(self):
        self.fail("Test was run, but setUp should have raises an error")
