from __future__ import division
from django.test.simple import DjangoTestSuiteRunner
from django_hudson.externals import unittest, etree
from django_hudson.plugins import trigger_plugin_signal
from django.utils.encoding import smart_unicode

import datetime
import itertools
import re

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6

class XMLTestResult(unittest.TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        super(XMLTestResult, self).__init__(stream, descriptions, verbosity)

        self._start_times = {}
        self._elements = {}

    def startTestRun(self):
        super(XMLTestResult, self).startTestRun()

        elem = etree.Element("testsuite")
        self._suite_start_time = datetime.datetime.utcnow()
        elem.set("timestamp", self._suite_start_time.isoformat())
        self._doc = etree.ElementTree(element=elem)
        self._suite = elem

    def startTest(self, test):
        super(XMLTestResult, self).startTest(test)
        self._start_times[test] = datetime.datetime.utcnow()

    def addError(self, test, err):
        super(XMLTestResult, self).addError(test, err)
        testcase = self._testcase(test)
        failure = etree.Element("error")
        failure.set("type", err[0].__name__)
        failure.set("message", smart_unicode(err[1]))
        testcase.append(failure)
        self._elements[test] = testcase

    def addFailure(self, test, err):
        super(XMLTestResult, self).addFailure(test, err)
        testcase = self._testcase(test)
        failure = etree.Element("failure")
        failure.set("type", err[0].__name__)
        failure.set("message", smart_unicode(err[1]))
        testcase.append(failure)
        self._elements[test] = testcase

    def stopTest(self, test):
        endtime = datetime.datetime.utcnow()
        if test not in self._elements:
            self._elements[test] = self._testcase(test)

        testcase = self._elements[test]
        testcase.set("time", "%.5f" % total_seconds(endtime - self._start_times[test]))

#        if self.buffer:
#            stdout = etree.Element("system-out")
#            stdout.text = self._stdout_buffer.getvalue()
#            testcase.append(stdout)
#            stderr = etree.Element("system-err")
#            stderr.text = self._stderr_buffer.getvalue()
#            testcase.append(stderr)
#
#            # never output to stdout
#            self._mirrorOutput = False

        self._suite.append(testcase)
        super(XMLTestResult, self).stopTest(test)

    def _testcase(self, test, **kwargs):
        elem = etree.Element("testcase", **kwargs)
        elem.set("name", test.id().rpartition('.')[2])
        elem.set("classname", test.id().rpartition('.')[0])
        return elem

    def stopTestRun(self):
        super(XMLTestResult, self).stopTestRun()

        suite = self._doc.getroot()
        suite.set("tests", str(self.testsRun))
        suite.set("failures", str(len(self.failures)))
        suite.set("errors", str(len(self.errors)))
        suite.set("time", "%.5f" % total_seconds(datetime.datetime.utcnow() - self._suite_start_time))

        for test, reason in self.skipped:
            elem = etree.Element("skipped")
            elem.text = reason
            self._elements[test].append(elem)

        for test, traceback in self.expectedFailures:
            elem = etree.Element("skipped")
            elem.text = traceback
            self._elements[test].append(elem)

        for test in self.unexpectedSuccesses:
            elem = etree.Element("skipped")
            elem.text = "This test is expected to fail, but it didn't."
            self._elements[test].append(elem)

        for test, traceback in self.failures:
            testcase = self._elements[test]
            failure = testcase.find("failure")
            if failure is None:
                failure = etree.Element("failure")
                failure.set("type", "Exception")
                failure.set("message", "")
                testcase.append(failure)
            failure.text = smart_unicode(traceback)

        for test, traceback in self.errors:
            testcase = self._elements[test]
            failure = testcase.find("error")
            if failure is None:
                failure = etree.Element("error")
                failure.set("type", "Exception")
                failure.set("message", "")
                testcase.append(failure)
            failure.text = smart_unicode(traceback)

class HudsonTestSuiteRunner(DjangoTestSuiteRunner):
    def __init__(self, *args, **kwargs):
        self._excludes = kwargs.pop('excludes')
        super(HudsonTestSuiteRunner, self).__init__(*args, **kwargs)

    def setup_databases(self):
        trigger_plugin_signal("before_database_setup")
        return super(HudsonTestSuiteRunner, self).setup_databases()

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        trigger_plugin_signal("before_suite_build", test_labels)
        suite = super(HudsonTestSuiteRunner, self).build_suite(test_labels, extra_tests, **kwargs)
        filtered_suite = unittest.TestSuite()
        for case in suite:
            exclude = False
            print case.id()
            for expr in self._excludes:
                if re.match(expr, case.id()):
                    exclude = True
                    break
            if not exclude:
                filtered_suite.addTest(case)
        return filtered_suite

    def run_suite(self, suite, **kwargs):
        test_runner = unittest.TextTestRunner(
                verbosity=self.verbosity,
                failfast=self.failfast,
                buffer=False,
                resultclass=XMLTestResult)

        trigger_plugin_signal("before_suite_run", suite)
        result = test_runner.run(suite)
        trigger_plugin_signal("after_suite_run", suite, result)
        return result

    def suite_result(self, suite, result, **kwargs):
        return result
