"""
.. include:: ../../README.md
"""

from collections import namedtuple

__title__ = 'functional-python'
__author__ = 'Peter Zaitcev / USSX Hares'
__license__ = 'BSD 2-clause'
__copyright__ = 'Copyright 2019 Peter Zaitcev'
__version__ = '0.2.1'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(*__version__.split('.'), releaselevel='alpha', serial=0)

from .final import *
from .predef import *

from .anyval import *
from .option import *

# The following modules are only available by direct import:
#  * builtins_wrapper
#  * chaintools
#  * containers
#  * dcj_support
#  * monads
#  * typing_wrapper
#  * util

__all__ = \
[
    'version_info',
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
    '__version__',
    *final.__all__,
    *predef.__all__,
    *anyval.__all__,
    *option.__all__,
]

# Suppress documentation generation for the root module.
__pdoc__ = { k: False for k in __all__ if not k.startswith('__') }
del __pdoc__['version_info']
del __pdoc__['OptionNone']
del __pdoc__['none']
