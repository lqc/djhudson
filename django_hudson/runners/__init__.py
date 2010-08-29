from __future__ import division
from django_hudson.externals import unittest
from xml.etree import ElementTree as etree
import datetime
import itertools

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6

class XMLTestResult(unittest.TestResult):

    def __init__(self, stream, descriptions, verbosity):
        super(XMLTestResult, self).__init__()

        self.successes = []
        self._start_times = {}
        self._elements = {}

    def startTestRun(self):
        super(XMLTestResult, self).startTestRun()
        self.buffer = True

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
        failure.set("message", str(err[1]))
        testcase.append(failure)
        self._elements[test] = testcase

    def addFailure(self, test, err):
        super(XMLTestResult, self).addFailure(test, err)
        testcase = self._testcase(test)
        failure = etree.Element("failure")
        failure.set("type", err[0].__name__)
        failure.set("message", str(err[1]))
        testcase.append(failure)
        self._elements[test] = testcase

    def stopTest(self, test):
        endtime = datetime.datetime.utcnow()
        if test not in self._elements:
            self._elements[test] = self._testcase(test)

        testcase = self._elements[test]
        testcase.set("time", "%.5f" % total_seconds(endtime - self._start_times[test]))

        if self.buffer:
            stdout = etree.Element("system-out")
            stdout.text = self._stdout_buffer.getvalue()
            testcase.append(stdout)
            stderr = etree.Element("system-err")
            stderr.text = self._stderr_buffer.getvalue()
            testcase.append(stderr)

            # never output to stdout
            self._mirrorOutput = False

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

        for test, _reason in self.skipped:
            self._elements[test].set("skipped", "True")

        for test, _traceback in self.expectedFailures:
            self._elements[test].set("skipped", "True")

        for test in self.unexpectedSuccesses:
            self._elements[test].set("skipped", "True")

        for test, traceback in self.failures:
            testcase = self._elements[test]
            testcase.find("failure").text = traceback

        for test, traceback in self.errors:
            testcase = self._elements[test]
            testcase.find("error").text = traceback
