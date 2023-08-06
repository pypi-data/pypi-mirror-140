# This file is imported from __init__.py and exec'd from setup.py

MAJOR = 2
MINOR = 1
MICRO = 0
RELEASE = False

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not RELEASE:
    # if it's a rcx release, it's not proceeded by a period. If it is a
    # devx release, it must start with a period
    __version__ += 'rc2'


_kivy_git_hash = '435c1ce7ecc40b9a1aa9922e1a7e63d6fa636700'
_kivy_build_date = '20220301'
