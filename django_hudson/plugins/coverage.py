from __future__ import with_statement, absolute_import

import os.path
import sys
import xml.dom.minidom
import re

from django_hudson.plugins import register, DisablePlugin
from django_hudson.externals import coverage
from functools import partial

if coverage:
    from coverage.xmlreport import XmlReporter

    class CoberturaCoverageReporter(XmlReporter):

        def xml_file(self, cu, analysis):
            super(CoberturaCoverageReporter, self).xml_file(cu, analysis)

#            pkg_name, fname = os.path.split(cu.name)
#            pkg_name = pkg_name or '.'
#
#            class_node = self.packages[pkg_name][0][fname.replace('.', '_')]
#            print class_node, fname, pkg_name

@register
class CoveragePlugin(object):

    def __init__(self):
        if coverage is None:
            raise DisablePlugin("No coverage module.")

    def configure(self, settings, options):
        self._coverage = coverage.coverage(
            config_file=options["coverage_config_file"],
            branch=options["coverage_measure_branch"],
            # source=settings.INSTALLED_APPS,
            cover_pylib=False,
        )

        self._output_file = options["coverage_report_file"]

        def excluded(app):
            for expr in getattr(settings, 'TEST_EXCLUDES', []):
                if re.match(expr, app):
                    return True
            for expr in getattr(settings, 'TEST_COVERAGE_EXCLUDES', []):
                if re.match(expr, app):
                    return True
            return False
        self.cover_apps = [app for app in settings.INSTALLED_APPS if not excluded(app)]

    def before_suite_run(self, suite):
        self._coverage.start()

    def after_suite_run(self, suite, result):
        self._coverage.stop()

        modules = filter(partial(self.want_module, suite), sys.modules.values())

        with open(self._coverage.config.xml_output, "wb") as outfile:
            reporter = CoberturaCoverageReporter(self._coverage,
                                             self._coverage.config.ignore_errors)
            reporter.report(modules,
                outfile=outfile,
                config=self._coverage.config
            )

    def want_module(self, allowed_apps, module):
        if not module or not hasattr(module, '__file__'):
            return False

        # report only modules inside installed applications        
        return any(module.__name__.startswith(app) for app in self.cover_apps)


    def add_options(self, group):
        group.add_option("--coverage-output",
                dest="coverage_report_file",
                default="coverage.xml",
                help="File to which coverage output should be reported. Default: '%default'")
        group.add_option("--coverage-config",
                dest="coverage_config_file", default=True,
                help="Configuration file for coverage module. Default: '%default'.")
        group.add_option("--coverage-no-branch-measure",
                action="store_false", default=True,
                dest="coverage_measure_branch",
                help="Don't measure branch coverage.")
