from __future__ import absolute_import

import os
import sys
import xml.dom
import re
import time

from django_hudson.plugins import register, DisablePlugin
from django_hudson.externals import coverage
from functools import partial

if coverage:
    """
        The following XMLReporter code is based on original XMLReporter from
        coverage.py by Ned Batchelder and Cobertura source code[1].
        
        [1]: https://cobertura.svn.sourceforge.net/svnroot/cobertura/trunk/cobertura/src/net/sourceforge/cobertura/reporting/xml/XMLReport.java
    """
    from coverage import __version__ as coverage_version
    from coverage.report import Reporter

    class CoberturaCoverageReporter(Reporter):
        """A reporter for writing Cobertura-style XML coverage results."""

        XMLSCHEMA_NS = "http://www.w3.org/2001/XMLSchema-instance"
        COBERTURA_NS = "http://cobertura.sourceforge.net"
        COBERTURA_DTD = "http://cobertura.sourceforge.net/xml/coverage-04.dtd"

        # The Schema seems very incomplete, so omit it
        # COBERTURA_SCHEMA = "http://cobertura.sourceforge.net/xml/coverage.xsd"

        def __init__(self, coverage, ignore_errors=False):
            super(CoberturaCoverageReporter, self).__init__(coverage, ignore_errors)
            self.arcs = coverage.data.has_arcs()

        def create_document(self):
            impl = xml.dom.getDOMImplementation()
            doctype = impl.createDocumentType("coverage", None, self.COBERTURA_DTD)
            document = impl.createDocument(self.COBERTURA_NS, "coverage", doctype)

            if hasattr(self, "COBERTURA_SCHEMA"):
                document.documentElement.setAttributeNS(self.XMLSCHEMA_NS,
                                            "schemaLocation", self.COBERTURA_SCHEMA)

            document.documentElement.setAttribute("version", coverage_version)
            # Timestamp in milliseconds
            document.documentElement.setAttribute("timestamp", unicode(int(time.time()*1000)))
            document.documentElement.setAttribute("complexity", "0")
            return document

        def create_sources_definition(self):
            self.sources_element = self.create_element("sources")
            for path in sys.path:
                e = self.create_element("source")
                e.appendChild(self.document.createTextNode(path))
                self.sources_element.appendChild(e)
            # self.sources_map = {}
            return self.sources_element

        def create_packages_definition(self):
            self.packages_element = self.create_element("packages")
            self.packages_map = {}
            return self.packages_element

        def create_empty_package(self, **kwargs):
            defaults = {"complexity": 0}
            defaults.update(kwargs)
            package_elem = self.create_element("package", **defaults)
            classes_elem = self.create_element("classes")
            package_elem.appendChild(classes_elem)
            return package_elem, classes_elem

        def create_empty_class(self, **kwargs):
            defaults = {"complexity": 0}
            defaults.update(kwargs)
            class_element = self.create_element("class", **defaults)
            class_element.appendChild(self.create_element("methods"))
            lines_element = self.create_element("lines")
            class_element.appendChild(lines_element)
            return class_element, lines_element

        def create_element(self, tagname, **kwargs):
            element = self.document.createElementNS(self.COBERTURA_NS, tagname)
            for key, value in kwargs.iteritems():
                element.setAttribute(key, unicode(value))
            return element

        def aggregate_packages(self):
            lines, branches = [0, 0], [0, 0] # total, hits            
            for package_element, _, classes_map in self.packages_map.itervalues():
                pkg_lines, pkg_branches = self.aggregate_package(package_element, classes_map)
                lines[0] += pkg_lines[0]
                lines[1] += pkg_lines[1]
                branches[0] += pkg_branches[0]
                branches[1] += pkg_branches[1]

            self.packages_element.setAttribute("line-rate", self.rate(*lines))
            self.packages_element.setAttribute("branch-rate", self.rate(*branches))
            return lines, branches

        def aggregate_package(self, package_element, classes_map):
            lines, branches = [0, 0], [0, 0]
            for _, _, metadata in classes_map.values():
                lines[0] += metadata["lines"][0]
                lines[1] += metadata["lines"][1]
                branches[0] += metadata["branches"][0]
                branches[1] += metadata["branches"][1]
            package_element.setAttribute("line-rate", self.rate(*lines))
            package_element.setAttribute("branch-rate", self.rate(*branches))
            return lines, branches

        def rate(self, total, misses):
            """Return the fraction of `hit`/`num`, as a string."""
            if not total: return "1"
            return "%.4g" % (float(total - misses) / float(total))

        def report(self, morfs, outfile=None, config=None):
            """Generate a Cobertura-compatible XML report for `morfs`.
    
            `morfs` is a list of modules or filenames.    
            `outfile` is a file object to write the XML to.
            `config` is a CoverageConfig instance.
    
            """
            self.generate_document(morfs, config)
            outfile = outfile or sys.stdout
            outfile.write(self.document.toprettyxml())

        def generate_document(self, morfs, config):
            self.document = self.create_document()
            self.coverage_element = self.document.documentElement
            self.coverage_element.appendChild(self.create_sources_definition())
            self.coverage_element.appendChild(self.create_packages_definition())

            self.report_files(self.report_code_unit, morfs, config)

            # append packages in ordered fashion
            for _, info in sorted(self.packages_map.iteritems(), key=lambda x: x[0]):
                self.packages_element.appendChild(info[0])

            lines, branches = self.aggregate_packages()

            self.coverage_element.setAttribute("lines-valid", unicode(lines[0]))
            self.coverage_element.setAttribute("lines-covered", unicode(lines[0] - lines[1]))
            self.coverage_element.setAttribute("line-rate", self.rate(*lines))
            self.coverage_element.setAttribute("branches-valid", unicode(branches[0]))
            self.coverage_element.setAttribute("branches-covered", unicode(branches[0] - branches[1]))
            self.coverage_element.setAttribute("branch-rate", self.rate(*branches))

        def report_code_unit(self, cu, analysis):
            """
                Add information about a single code unit to the report.                                
            """
            classname = cu.modname
            if classname.endswith("."):
                classname = classname[:-1]

            if cu.filename.endswith("__init__.py"):
                pkgname = classname
                classname = "__init__"
            else:
                pkgname, _, classname = classname.rpartition(".")

            try:
                package_element, classes_element, classes_map = self.packages_map[pkgname]
            except KeyError:
                package_element, classes_element = self.create_empty_package(name=pkgname)
                classes_map = {}
                self.packages_map[pkgname] = package_element, classes_element, classes_map


            filename = None
            for path in sys.path:
                relative = os.path.relpath(cu.filename, path)
                if not relative.startswith('..'):
                    filename = relative
                    break
            if filename is None:
                filename = cu.name

            # TODO
            try:
                class_element, lines_element, metadata = classes_map[classname]
            except KeyError:
                class_element, lines_element = self.create_empty_class(
                            name=classname, filename=filename, complexity=0)
                metadata = {}
                classes_map[classname] = class_element, lines_element, metadata
                classes_element.appendChild(class_element)

            branch_stats = analysis.branch_stats()
            metadata["branches"] = [0, 0] # hit / miss

            # For each statement, create an XML 'line' element.
            for line in analysis.statements:
                line_element = self.create_element("line", number=unicode(line))
                # Q: can we get info about the number of times a statement is
                # executed?  If so, that should be recorded here.
                line_element.setAttribute("hits", unicode(int(line not in analysis.missing)))
                if self.arcs and line in branch_stats:
                    total, taken = branch_stats[line]
                    line_element.setAttribute("branch", "true")
                    line_element.setAttribute("condition-coverage",
                        "%d%% (%d/%d)" % (100 * taken / total, taken, total)
                    )
                    metadata["branches"][0] += total
                    metadata["branches"][1] += total - taken
                lines_element.appendChild(line_element)

            metadata["lines"] = len(analysis.statements), len(analysis.missing)
            class_element.setAttribute("line-rate", self.rate(*metadata["lines"]))
            class_element.setAttribute("branch-rate", self.rate(*metadata["branches"]))


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
        self._html_dir = options["coverage_html_report_dir"]

        def excluded(app):
            if app.startswith("django_hudson") and not options["X_cover_django_hudson"]:
                return True
            for expr in getattr(settings, 'TEST_EXCLUDES', []):
                if re.match(expr, app):
                    return True
            for expr in getattr(settings, 'TEST_COVERAGE_EXCLUDES', []):
                if re.match(expr, app):
                    return True
            return False
        self.cover_apps = set([app for app in settings.INSTALLED_APPS if not excluded(app)])

    def before_suite_build(self, *args, **kwargs):
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

        if self._html_dir:
            self._coverage.html_report(modules, directory=self._html_dir)

    def want_module(self, suite, module):
        if not module or not hasattr(module, '__file__'):
            return False

        # report only modules inside installed applications        
        return any(module.__name__.startswith(app) for app in self.cover_apps)


    def add_options(self, group):
        group.add_option("--X-cover-self",
                dest="X_cover_django_hudson",
                action="store_true", default=False,
                help="Should django_hudson report coverage of itself. This usually makes no sense,"
                " so it's disabled by default.")
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
        group.add_option("--coverage-html-report",
                dest="coverage_html_report_dir",
                default="",
                help="Directory to which HTML coverage report should be written. If not specified, no report is generated.")
