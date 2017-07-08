from os import path
from pgallery import thumb
from pgallery.config import Config

from pgallery.image import ThumbImage, Dimension
from pgallery.sys import execute

backblur = int((thumb.min_size.x + thumb.min_size.y) / 2 * 0.1)
backsize = Dimension(int(thumb.min_size.x * 4), int(thumb.min_size.y * 3))


def create(image: ThumbImage, output_dir, relative_dir, config: Config):
    destination = path.join(output_dir, 'blurs', relative_dir,
                            path.basename(image.original.path))

    execute(['convert', '-quiet', image.thumb.path,
             '-virtual-pixel', 'Mirror',
             '-gaussian-blur', '0x%s' % backblur,
             '-scale', "%sx%s" % (backsize.x, backsize.y),
             '-quality', '90',
             destination], config)
