MAJOR = 0
MINOR = 4
MICRO = 2
IS_RELEASED = True

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not IS_RELEASED:
    __version__ += '.dev0'
