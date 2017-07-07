from os import path
from pgallery.sys import execute
from pgallery.image import Image, Dimension


def create(image: Image, output_folder, relative_dir):
    max_full_size = Dimension(1600, 1200)
    image_quality = 90

    destination = path.join(output_folder, 'imgs', relative_dir,
                            path.basename(image.original.path))

    cmd = ['convert',
           '-quiet',
           image.original.path,
           '-gamma', '0.454545',
           '-geometry', '%sx%s>' % (max_full_size.x, max_full_size.y),
           '-print', '%w %h',
           '-gamma', '2.2',
           '+profile', '!icc,*',
           '-quality',
           str(image_quality),
           destination
           ]
    completed_process = execute(cmd)
    (width_bytes, height_bytes) = completed_process.stdout.split(b' ')

    return Dimension(int(width_bytes), int(height_bytes))
