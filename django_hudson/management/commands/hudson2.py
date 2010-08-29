# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
import sys

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--failfast', action='store_true', dest='failfast', default=False,
            help='Tells Django to stop running the test suite after first failed test.'),
        make_option('--test-report', dest='xml_report_file', default="unittests.xml",
            help='File to which jUnit report should be written.')
    )
    help = 'Runs the test suite for the specified applications, or the entire site if no apps are specified.'
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner
        from django_hudson.runners import HudsonTestSuiteRunner

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)
        failfast = options.get('failfast', False)
        TestRunner = get_runner(settings)

        if not issubclass(TestRunner, HudsonTestSuiteRunner):
            print 'Your test runner is not a subclass of HudsonTestSuiteRunner (switching to it now).'
            TestRunner = HudsonTestSuiteRunner

        test_runner = TestRunner(verbosity=verbosity,
                                 interactive=interactive,
                                 failfast=failfast)

        result = test_runner.run_tests(test_labels)
        result._doc.write(options["xml_report_file"], encoding='utf-8')

        if result.failures:
            sys.exit(1)
