from os import path
from pgallery.image import Dimension, ScaledownImage, ThumbImage
from pgallery.sys import execute

thumb_quality = 90
min_size = Dimension(150.0, 112.0)  # Use floats for floating precision below
max_size = Dimension(267.0, 200.0)  # Use floats for floating precision below


def create(image: ScaledownImage, output_folder, relative_dir):
    working_image = image.scaledown
    destination = path.join(output_folder, 'thumbs', relative_dir,
                            path.basename(working_image.path))

    if working_image.size.x / working_image.size.y < min_size.x / min_size.y:
        thumb_ratio = min_size.x / working_image.size.x
    else:
        thumb_ratio = min_size.y / working_image.size.y

    sthumb = Dimension(max(round(working_image.size.x * thumb_ratio), min_size.x),
                       max(round(working_image.size.y * thumb_ratio), min_size.y))

    mthumb = Dimension(min(max_size.x, sthumb.x), min(max_size.y, sthumb.y))

    # face/center detection
    center = Dimension(0.5, 0.5)

    def clamp(a, b, v):
        return max(a, min(b, v))

    # cropping window
    dx = sthumb.x - mthumb.x
    cx = clamp(0, dx, int(center.x * sthumb.x - sthumb.x / 2 + dx / 2))
    dy = sthumb.y - mthumb.y
    cy = clamp(0, dy, int(center.y * sthumb.y - sthumb.y / 2 + dy / 2))

    cmd = ['convert',
           '-quiet', working_image.path,
           '-gamma', '0.454545',
           '-resize', '%sx%s!' % (sthumb.x, sthumb.y),
           '-gravity', 'NorthWest',
           '-crop', '%sx%s+%s+%s' % (mthumb.x, mthumb.y, cx, cy),
           '-gamma', '2.2',
           '+profile', '!icc,*',
           '-quality', str(thumb_quality),
           destination
           ]
    execute(cmd)
    return ThumbImage(image, destination, mthumb)
