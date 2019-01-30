from datetime import datetime
from typing import Optional

from pgallery.image import Dimension


def create_thumbdto(min_size: Dimension, max_size: Dimension):
    return {
        'min': min_size,
        'max': max_size
    }


def create_rootdto(images, thumb, blur: Dimension):
    return {
        'version': '1.8.2',
        'data': sorted(images, key=lambda img: img['date']),
        'thumb': thumb,
        'blur': blur
    }


def create_datadto(filename, img_size: Dimension, thumb_size: Dimension, file_size: Dimension,
                   taken_date: Optional[datetime]):
    def type_size(file_type: str, size: Dimension):
        return [
            '%s/%s' % (file_type, filename),
            [
                size.x,
                size.y
            ]
        ]

    return {
        'blur': 'blurs/%s' % filename,
        'img': type_size('imgs', img_size),
        'thumb': type_size('thumbs', thumb_size),
        'file': type_size('files', file_size),
        'date': taken_date.strftime('%Y-%m-%d %H:%M') if taken_date else None,
        'stamp': int(datetime.now().timestamp()),
    }
