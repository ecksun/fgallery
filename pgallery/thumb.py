from os import path
from pgallery.sys import execute
from pgallery.image import Image, Dimension

thumb_quality = 90
min_size = Dimension(150.0, 112.0)  # Use floats for floating precision below
max_size = Dimension(267.0, 200.0)  # Use floats for floating precision below


def create(image: Image, output_folder, relative_dir):
    destination = path.join(output_folder, 'thumbs', relative_dir, path.basename(image.path))

    if image.size.x / image.size.y < min_size.x / min_size.y:
        thumb_ratio = min_size.x / image.size.x
    else:
        thumb_ratio = min_size.y / image.size.y

    sthumb = Dimension(max(round(image.size.x * thumb_ratio), min_size.x),
                       max(round(image.size.y * thumb_ratio), min_size.y))

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
           '-quiet', image.path,
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
    return mthumb
