# __init__.py
import sys

# Check compatibility
if ( sys.version_info > (3, 2) ):
  raise "Requires Python 3.2!"

# Python 3.2 only
# nfcdaemon is compatible only with Python 3.2+
__all__ = ['nfcdaemon']
