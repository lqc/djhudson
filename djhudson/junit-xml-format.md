Notes on XML read by Hudson CI
==============================

There are various dialects of what is commonly known as jUnit XML reports. 
The format itself was actually introduced by an Ant task, not jUnit itself and
has no formal specification. Other tools like TestNG or gtest use variants
of this format.


Test suites
-----------

A report can contain a single <testsuite /> or a collection nested in a <testsuites /> element.

Attributes:

  * name - for example, the name of the class containing test cases
  * package (optional) - package containing this test suite 
  * time - seconds spent of running the suite in %.3f format
  * timestamp - date & time when the suite was started in ISO-8601 format
  * tests - total number of tests runned
  * failures - numer of tests that failed assertions
  * errors - number of tests that failed due to unexpected errors
  
If package is present, Hudson will display "package + . + name" as the suite's name.
  
Children:

  * One <testcase /> for each test case in the suite.
  * <system-out /> and <system-err /> containing buffered output.


Test cases
-----------

Attributes:

  * classname - name of the class containing this test.
  * name - name of the test. 
  * time - timing of this test as a float.
  * skipped - if present, test is treated as skipped.
 
Children:
  * <error /> or <failure /> - error or failure report.
  * <system-out />, <system-err />
  
<error> and <failure> have a "message" attribute which is a short description, "type" which
is the type of failure. Full stacktrace should be contained in their text as CDATA
