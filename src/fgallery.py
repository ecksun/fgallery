#!/usr/bin/python3

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

import subprocess

import exifread
import os
import shutil
from collections import namedtuple
from os import path

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('input', help='Input directory')
parser.add_argument('output', help='Output directory to write gallery to')

args = parser.parse_args()

if not path.isdir(args.input):
    print('input directory "%s" is not a directory' % args.input, file=sys.stderr)
    sys.exit(1)


def copy_template_files(output):
    root_folder = path.join(path.dirname(path.abspath(__file__)), path.pardir)
    template_dir = path.join(root_folder, 'view')
    shutil.rmtree(output)
    shutil.copytree(template_dir, output)


def files_in_dir(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield path.join(dirpath, filename)


copy_template_files(args.output)

Dimension = namedtuple('Dimension', 'x y')


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


def create_rootdto(images, thumb, blur: Dimension):
    return {
        'version': '1.8.2',
        'data': images,
        'thumb': thumb,
        'blur': blur
    }


def create_thumbdto(min_size: Dimension, max_size: Dimension):
    return {
        'min': min_size,
        'max': max_size
    }


def images_to_process(directory):
    for file in files_in_dir(directory):
        yield file


def get_exif(image):
    with open(image, 'rb') as fd:
        return exifread.process_file(fd, details=False)


class Image:
    def __init__(self, image_path):
        self.path = image_path
        self.exif_tags = get_exif(self.path)

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


def process_image(image_path):
    image = Image(image_path)
    if not image.taken_date:
        print('Failed to parse taken_date from %s' % image.path, file=sys.stderr)
        return
    if not image.size:
        print('Failed to parse size of %s' % image.path, file=sys.stderr)
        return
    relative_path = path.relpath(image.path, args.input)
    relative_dir = path.dirname(relative_path)

    create_folders(relative_dir)

    scaledown_size = create_scaledown(image, relative_dir)
    thumb_size = create_thumb(image, relative_dir)
    create_original(image, relative_dir)

    return create_datadto(relative_path, scaledown_size, thumb_size, image.size, image.taken_date)


def create_original(image: Image, relative_dir):
    shutil.copy(image.path, path.join(args.output, 'files', relative_dir))


def create_thumb(image: Image, relative_dir):
    thumb_quality = 90
    min_thumb_size = Dimension(150.0, 112.0)  # Use floats for floating precision below
    max_thumb_size = Dimension(267.0, 200.0)  # Use floats for floating precision below

    destination = path.join(args.output, 'thumbs', relative_dir, path.basename(image.path))

    if image.size.x / image.size.y < min_thumb_size.x / min_thumb_size.y:
        thumb_ratio = min_thumb_size.x / image.size.x
    else:
        thumb_ratio = min_thumb_size.y / image.size.y

    sthumb = Dimension(max(round(image.size.x * thumb_ratio), min_thumb_size.x),
                       max(round(image.size.y * thumb_ratio), min_thumb_size.y))

    mthumb = Dimension(min(max_thumb_size.x, sthumb.x), min(max_thumb_size.y, sthumb.y))

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


def execute(cmd):
    print(cmd)
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=True)


def create_scaledown(image: Image, relative_dir):
    max_full_size = Dimension(1600, 1200)
    image_quality = 90

    destination = path.join(args.output, 'imgs', relative_dir, path.basename(image.path))

    cmd = ['convert',
           '-quiet',
           image.path,
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


def main():
    datas = [process_image(image) for image in images_to_process(args.input)]
    datas = [data for data in datas if data]

    with open(path.join(args.output, 'data.json'), mode='w', encoding='utf-8') as f:
        f.write(json.dumps(create_rootdto(images=datas,
                                          thumb=create_thumbdto(Dimension(100, 100),
                                                                Dimension(200, 200)),
                                          blur=Dimension(100, 200))))


def create_folders(target_dir):
    for directory in ('imgs', 'thumbs', 'files'):
        os.makedirs(path.join(args.output, directory, target_dir), exist_ok=True)


main()
