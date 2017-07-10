"""
YasenBaka
~~~~~~~~~~~~~~~~~~~
YasenBaka, a multifunctional Discord bot with special World of Warships commands
:copyright: (c) Copyright 2016-2017 MaT1g3R
:license: Apache License 2.0, see LICENSE for more details.
"""
from collections import namedtuple

from bot.session_manager import HTTPStatusError, SessionManager
from bot.yasen import Yasen

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(
    major=0, minor=9, micro=0, releaselevel='beta', serial=0
)

__title__ = 'YasenBaka'
__author__ = 'ラブアローシュート#6728'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2016-2017 MaT1g3R'
__version__ = '.'.join([str(i) for i in list(version_info)[:3]])

__all__ = ['HTTPStatusError', 'SessionManager', 'Yasen', 'version_info',
           '__title__', '__author__', '__license__',
           '__copyright__', '__version__']
