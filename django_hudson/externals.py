"""
    Compatibility hacks for external modules.
"""
try:
    import coverage
except ImportError:
    coverage = None

import sys

if sys.version[:3] < (2, 7):
    try:
        import unittest2 as unittest
    except ImportError:
        print >> sys.stderr, """ERROR: This package requires unittest2 module which was added to stdlib in Python 2.7.
You can either install unittest2 from PyPI or upgrade your Python."""
        sys.exit(1)
else:
    # Python 2.7 is good enough
    import unittest

try:
    # First try LXML
    from lxml import etree
except ImportError:
    try:
        from xml.etree import cElementTree as etree
    except ImportError:
        print >> sys.stderr, """ERROR: Couldn't find ElementTree package, which is required for XML reporting."""
        sys.exit(1)

__all__ = (
    'unittest',
    'coverage',
    'etree'
)


