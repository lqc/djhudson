from django_hudson.externals import unittest
from django_hudson.runners import XMLTestResult
from cStringIO import StringIO
import time

from xml.etree import ElementTree as etree

# This is a bit meta ;)
class XMLTestResultTestCase(unittest.TestCase):

    def setUp(self):
        self.buffer = StringIO()
        self.runner = unittest.TextTestRunner(stream=self.buffer, resultclass=XMLTestResult)

    def run_testcase(self, test_case_class):
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case_class)
        result = self.runner.run(suite)
        self.assertIsInstance(result, XMLTestResult)
        return result

    def is_iso8601_time(self, string):
        base, _dot, rest = string.rpartition('.')
        time.strptime(base, "%Y-%m-%dT%H:%M:%S")
        if not _dot:
            return rest == ''
        try:
            return int(rest) > 0
        except ValueError:
            return False

    def test_no_tests(self):
        class EmptyTestCase(unittest.TestCase):
            pass

        result = self.run_testcase(EmptyTestCase)
        self.assertIsInstance(result, XMLTestResult)

        suite = result._doc.getroot()
        self.assertEqual(suite.get("tests"), "0")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "0")
        self.assertTrue(self.is_iso8601_time(suite.get("timestamp")))


    def test_success(self):
        class SimpleTestCase(unittest.TestCase):
            def test_success(self):
                self.assertTrue(True)
        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._doc.getroot()
        self.assertEqual(suite.get("tests"), "1")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "0")

        testcase = suite.find("testcase")
        self.assertEqual(testcase.get("name"), "test_success")
        self.assertEqual(testcase.get("classname"), "hudson.tests.SimpleTestCase")
        self.assertGreaterEqual(float(testcase.get("time")), 0)
        self.assertEqual(len(list(testcase)), 2)

    def test_failure(self):
        class SimpleTestCase(unittest.TestCase):
            def test_failure(self):
                self.assertFalse(True)
        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._suite
        self.assertEqual(suite.get("tests"), "1")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "1")

        testcase = suite.find("testcase")
        errors = testcase.findall("failure")
        error = errors[0]
        self.assertListEqual(errors, [error], "Test case should have only one error report.")
        self.assertEqual(error.get("type"), "AssertionError")

    def test_error(self):
        class SimpleTestCase(unittest.TestCase):
            def test_division_by_zero(self):
                self.assertTrue(1 / 0)
        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._suite
        self.assertEqual(suite.get("tests"), "1")
        self.assertEqual(suite.get("errors"), "1")
        self.assertEqual(suite.get("failures"), "0")

        testcase = suite.find("testcase")
        errors = testcase.findall("error")
        error = errors[0]
        self.assertListEqual(errors, [error], "Test case should have only one error report.")
        self.assertEqual(error.get("type"), "ZeroDivisionError")

    def test_skipping(self):
        class SimpleTestCase(unittest.TestCase):
            @unittest.skip("Because we can!")
            def test_skipped(self):
                self.assertTrue(True)

        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._suite
        self.assertEqual(suite.get("tests"), "1")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "0")

        testcase = suite.find("testcase")
        skipped = testcase.find("skipped")
        self.assertEqual(skipped.text, "Because we can!")

    def test_excepted_failure(self):
        class SimpleTestCase(unittest.TestCase):
            @unittest.expectedFailure
            def test_fail(self):
                self.assertEqual(1, 0, "broken")

            @unittest.expectedFailure
            def test_no_fail(self):
                self.assertEqual(0, 0, "broken")

        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._suite
        self.assertEqual(suite.get("tests"), "2")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "0")

        for testcase in suite.findall("testcase"):
            self.assertIsNotNone(testcase.find("skipped"))

    def test_output_buffering(self):
        class SimpleTestCase(unittest.TestCase):
            def test_noisy_stdout(self):
                print "Hello World!"
            def test_noisy_stderr(self):
                import sys
                print >> sys.stderr, "Hello World!"
        SimpleTestCase.__module__ = "hudson.tests"

        result = self.run_testcase(SimpleTestCase)
        suite = result._suite
        self.assertEqual(suite.get("tests"), "2")
        self.assertEqual(suite.get("errors"), "0")
        self.assertEqual(suite.get("failures"), "0")

        for testcase in suite.findall("testcase"):
            if testcase.get("name") == "test_noisy_stdout":
                self.assertEqual(testcase.find("system-out").text, "Hello World!\n")
            else:
                self.assertEqual(testcase.find("system-err").text, "Hello World!\n")
