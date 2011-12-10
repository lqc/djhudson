"""
    Compatibility hacks for external modules.
"""
try:
    import coverage
except ImportError:
    coverage = None

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
    'coverage',
    'etree'
)
