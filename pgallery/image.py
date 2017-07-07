from datetime import datetime

import exifread
from collections import namedtuple

Dimension = namedtuple('Dimension', 'x y')


class ImageFile:
    def __init__(self, path, size: Dimension):
        self.path = path
        self.size = size


class Image:
    @staticmethod
    def get_exif(image):
        with open(image, 'rb') as fd:
            return exifread.process_file(fd, details=False)

    def __init__(self, image_path, exif_tags):
        self.exif_tags = exif_tags
        self.original = ImageFile(image_path, self.size)

    @classmethod
    def from_path(cls, image_path):
        exif_tags = Image.get_exif(image_path)
        instance = cls(image_path, exif_tags)
        return instance

    @property
    def size(self):
        if 'EXIF ExifImageWidth' in self.exif_tags and 'EXIF ExifImageLength' in self.exif_tags:
            return Dimension(self.exif_tags['EXIF ExifImageWidth'].values[0],
                             self.exif_tags['EXIF ExifImageLength'].values[0])
        return None

    @property
    def taken_date(self):
        if 'EXIF DateTimeOriginal' in self.exif_tags:
            taken_tag = self.exif_tags['EXIF DateTimeOriginal']
            return datetime.strptime(str(taken_tag) + 'UTC', '%Y:%m:%d %H:%M:%S%Z')
        return None


