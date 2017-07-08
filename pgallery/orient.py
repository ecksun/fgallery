import sys

from pgallery.config import Config
from pgallery.sys import executable_exists, execute


# noinspection PyUnusedLocal
def auto_orient_support_missing(path, config):
    pass


def orient_with_exiftran(path, config: Config):
    return execute(['exiftran', '-aip', path], config)


def orient_with_exifautotran(path, config: Config):
    return execute(['exifautotran', path], config)


if executable_exists('exiftran'):
    orient = orient_with_exiftran
elif executable_exists('exifautotran'):
    orient = orient_with_exifautotran
else:
    print('Auto-orient not supported, requires either exiftran or exifautotran', file=sys.stderr)
    orient = auto_orient_support_missing
