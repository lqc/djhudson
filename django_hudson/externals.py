"""
    Compatibility hacks for external modules.
"""
import sys

__all__ = [
    'unittest'
]

if sys.version[:3] < (2, 7):
    try:
        import unittest2 as unittest
    except ImportError:
        print """This package requires unittest2 module which was added to stdlib in Python 2.7.
You can either install unittest2 from PyPI or upgrade your Python."""
        sys.exit(1)
else:
    # Python 2.7 is good enough
    import unittest
