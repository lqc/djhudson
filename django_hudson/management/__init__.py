from django_hudson import plugins
import sys

class CoveragePlugin(object):

    def __init__(self):
        try:
            import coverage
        except ImportError:
            raise plugins.DisablePlugin("No coverage module.")

    def configure(self, options):
        import coverage
        self._coverage = coverage.coverage(
            config_file=options["coverage_config_file"],
            branch=options["coverage_measure_branch"],
            cover_pylib=False,
        )

        self._output_file = options["coverage_report_file"]

    def before_suite_run(self, suite):
        self._coverage.start()

    def after_suite_run(self, suite, result):
        self._coverage.stop()

        self._coverage.xml_report(
            morfs=[plugins],
            outfile=self._output_file
        )

    def add_options(self, group):
        group.add_option("--coverage-output",
                dest="coverage_report_file",
                default="coverage.xml",
                help="File to which coverage output should be reported. Default: '%default'")
        group.add_option("--coverage-config",
                dest="coverage_config_file", default=".coveragerc",
                help="Configuration file for coverage module. Default: '%default'.")
        group.add_option("--coverage-no-branch-measure",
                action="store_false", default=True,
                dest="coverage_measure_branch",
                help="Don't measure branch coverage.")

CoveragePlugin = plugins.register(CoveragePlugin)
