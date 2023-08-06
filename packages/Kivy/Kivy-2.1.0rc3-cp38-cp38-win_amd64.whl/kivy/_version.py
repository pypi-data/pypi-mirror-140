# This file is imported from __init__.py and exec'd from setup.py

MAJOR = 2
MINOR = 1
MICRO = 0
RELEASE = False

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not RELEASE:
    # if it's a rcx release, it's not proceeded by a period. If it is a
    # devx release, it must start with a period
    __version__ += 'rc3'


_kivy_git_hash = 'fad37274913f3e0ad28bbcf76202bc06d08f730d'
_kivy_build_date = '20220301'

