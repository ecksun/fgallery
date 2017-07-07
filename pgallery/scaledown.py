from contextlib import contextmanager

import os
import shutil
from os import path
from pgallery.orient import orient
from pgallery.sys import execute
from pgallery.image import Image, Dimension, ScaledownImage


@contextmanager
def file_copy(file_path, dest):
    tmp_file_path = dest + '.tmp'
    shutil.copy2(file_path, tmp_file_path)
    yield tmp_file_path
    os.remove(tmp_file_path)


def create(image: Image, output_folder, relative_dir):
    max_full_size = Dimension(1600, 1200)
    image_quality = 90

    destination = path.join(path.join(output_folder, 'imgs', relative_dir),
                            path.basename(image.original.path))

    with file_copy(image.original.path, destination) as tmp_path:
        orient(tmp_path)
        size = scale_image(destination, tmp_path, image_quality, max_full_size)
        return ScaledownImage(image, destination, size)


def scale_image(destination, image_path, image_quality, max_full_size):
    cmd = ['convert',
           '-quiet',
           image_path,
           '-gamma', '0.454545',
           '-geometry', '%sx%s>' % (max_full_size.x, max_full_size.y),
           '-print', '%w %h',
           '-gamma', '2.2',
           '+profile', '!icc,*',
           '-quality', str(image_quality),
           destination
           ]
    completed_process = execute(cmd)
    (width_bytes, height_bytes) = completed_process.stdout.split(b' ')
    return Dimension(int(width_bytes), int(height_bytes))
