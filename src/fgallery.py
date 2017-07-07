#!/usr/bin/python3

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

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


def parse_taken_date(tags):
    if 'EXIF DateTimeOriginal' in tags:
        taken_tag = tags['EXIF DateTimeOriginal']
        return datetime.strptime(str(taken_tag) + 'UTC', '%Y:%m:%d %H:%M:%S%Z')


def get_dimensions(tags):
    if 'EXIF ExifImageWidth' in tags and 'EXIF ExifImageLength' in tags:
        return Dimension(tags['EXIF ExifImageWidth'].values[0],
                         tags['EXIF ExifImageLength'].values[0])


def main():
    for directory in ('imgs', 'thumbs', 'files'):
        os.makedirs(path.join(args.output, directory), exist_ok=True)

    datas = []

    for image in images_to_process(args.input):
        tags = get_exif(image)
        taken_date = parse_taken_date(tags)
        if not taken_date:
            print('Failed to parse taken_date from %s' % image, file=sys.stderr)
            continue
        size = get_dimensions(tags)
        if not size:
            print('Failed to parse size of %s' % image, file=sys.stderr)
            continue
        relative_path = path.relpath(image, args.input)
        relative_dir = path.dirname(relative_path)

        for directory in ('imgs', 'thumbs', 'files'):
            os.makedirs(path.join(args.output, directory, relative_dir), exist_ok=True)

        shutil.copy(image, path.join(args.output, 'imgs', relative_dir))
        shutil.copy(image, path.join(args.output, 'thumbs', relative_dir))
        shutil.copy(image, path.join(args.output, 'files', relative_dir))
        datas += [create_datadto(relative_path, size, size, size, taken_date)]

    with open(path.join(args.output, 'data.json'), mode='w', encoding='utf-8') as f:
        f.write(json.dumps(create_rootdto(images=datas,
                                          thumb=create_thumbdto(Dimension(100, 100),
                                                                Dimension(200, 200)),
                                          blur=Dimension(100, 200))))


main()
