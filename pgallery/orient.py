import sys

from pgallery.sys import executable_exists, execute


# noinspection PyUnusedLocal
def auto_orient_support_missing(path):
    pass


def orient_with_exiftran(path):
    return execute(['exiftran', '-aip', path])


def orient_with_exifautotran(path):
    return execute(['exifautotran', path])


if executable_exists('exiftran'):
    orient = orient_with_exiftran
elif executable_exists('exifautotran'):
    orient = orient_with_exifautotran
else:
    print('Auto-orient not supported, requires either exiftran or exifautotran', file=sys.stderr)
    orient = auto_orient_support_missing
