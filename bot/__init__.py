"""
Yasen-Baka
~~~~~~~~~~~~~~~~~~~
Yasen-Baka, a multifunctional Discord bot
with special World of Warships commands.
:copyright: (c) Copyright 2016-2017 MaT1g3R
:license: Apache License 2.0, see LICENSE for more details.
"""
from collections import namedtuple

from bot.anime_searcher import AnimeSearcher
from bot.yasen import Yasen

VersionInfo = namedtuple(
    'VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(
    major=1, minor=0, micro=0, releaselevel='release', serial=0
)

__title__ = 'Yasen-Baka'
__author__ = 'ラブアローシュート#6728'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2016-2017 MaT1g3R'
__version__ = '.'.join([str(i) for i in list(version_info)[:3]])
__url__ = 'https://github.com/MaT1g3R/YasenBaka'

__all__ = ['Yasen', 'version_info', 'AnimeSearcher', '__title__',
           '__author__', '__license__', '__copyright__',
           '__version__', '__url__']
