# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.core.management.base import BaseCommand
from optparse import make_option, OptionGroup
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
        from djhudson.runners import HudsonTestSuiteRunner
        from djhudson.plugins import trigger_plugin_signal

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', False)
        failfast = options.get('failfast', False)

        trigger_plugin_signal("configure", settings, options)

        # Lookup can import modules, so give coverage-like plugins a chance,
        # to do something before it.
        TestRunner = get_runner(settings)

        if not issubclass(TestRunner, HudsonTestSuiteRunner):
            TestRunner = type("DynamicHudsonRunner", (HudsonTestSuiteRunner, TestRunner), {})

        test_runner = TestRunner(verbosity=verbosity,
                                 interactive=interactive,
                                 failfast=failfast,
                                 excludes=getattr(settings, 'TEST_EXCLUDES', []))

        # filter test labels

        result = test_runner.run_tests(test_labels)
        result._doc.write(options["xml_report_file"], encoding='utf-8')

        trigger_plugin_signal("report", result, test_labels)

        if len(result.failures) + len(result.errors):
            sys.exit(1)

    def create_parser(self, *args):
        # extend the option list with plugin specific options
        from djhudson.plugins import get_plugins
        parser = super(Command, self).create_parser(*args)

        for plugin in get_plugins():
            option_group = OptionGroup(parser, getattr(plugin, "name", type(plugin).__name__), "")
            plugin.add_options(option_group)
            if option_group.option_list:
                parser.add_option_group(option_group)
        return parser



