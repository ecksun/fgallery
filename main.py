import argparse
import sys

import os
from os import path
from pgallery import fgallery
from pgallery.config import Config
from pgallery.image import Image

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('input', help='Input directory')
parser.add_argument('output', help='Output directory to write gallery to')
parser.add_argument('--link-original', help='Method for linking to the original file',
                    default='symlink', choices=['symlink', 'hardlink', 'copy'])
parser.add_argument('--verbose', help='Show verbose output', action='store_true')

args = parser.parse_args()

if not path.isdir(args.input):
    print('input directory "%s" is not a directory' % args.input, file=sys.stderr)
    sys.exit(1)


def files_in_dir(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield path.join(dirpath, filename)


def images_to_process(directory):
    for file in files_in_dir(directory):
        yield file


def valid_image(image: Image):
    if not image.taken_date:
        print('Failed to parse taken_date from %s' % image.original.path, file=sys.stderr)
        return False
    if not image.size:
        print('Failed to parse size of %s' % image.original.path, file=sys.stderr)
        return False
    return True


def main(config):
    images = [Image.from_path(image_path) for image_path in images_to_process(config.input_folder)]
    valid_images = [image for image in images if valid_image(image)]
    fgallery.copy_template_files(config.output_folder)
    fgallery.process_and_save(valid_images, config)

main(Config(args))
