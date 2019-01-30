#!/usr/bin/python3
import json

from multiprocessing.pool import Pool

from functools import partial

import os
import shutil
from os import path
from pgallery import thumb, scaledown, original, blur
from pgallery.config import Config
from pgallery.data_json import create_datadto, create_rootdto, create_thumbdto
from pgallery.image import Image


def copy_template_files(destination):
    root_folder = path.join(path.dirname(path.abspath(__file__)), path.pardir)
    template_dir = path.join(root_folder, 'view')
    if path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(template_dir, path.join(destination, 'view'))
    os.symlink(path.join('view', 'index.html'), path.join(destination, 'index.html'))

def process_image(image: Image, config: Config):
    relative_path = path.relpath(image.original.path, config.input_folder)
    relative_dir = path.dirname(relative_path)

    create_folders(config.output_folder, relative_dir)

    scaledown_image = scaledown.create(image, config.output_folder, relative_dir, config)
    thumb_image = thumb.create(scaledown_image, config.output_folder, relative_dir, config)
    original.create(image, config.output_folder, relative_dir, config)
    blur.create(thumb_image, config.output_folder, relative_dir, config)

    return create_datadto(relative_path, scaledown_image.scaledown.size, thumb_image.thumb.size,
                          image.size, image.taken_date)


def create_folders(output_dir, target_dir):
    for directory in ('imgs', 'thumbs', 'files', 'blurs'):
        os.makedirs(path.join(output_dir, directory, target_dir), exist_ok=True)


def process_images(config: Config, images: [Image]):
    process = partial(process_image, config=config)
    # datas = list(map(process, images))
    with Pool(processes=None) as p:
        datas = (p.map(process, images))

    return create_rootdto(images=datas,
                          thumb=create_thumbdto(thumb.min_size,
                                                thumb.max_size),
                          blur=blur.backsize)


def process_and_save(images: [Image], config: Config):
    data_dto = process_images(config, images)

    with open(path.join(config.output_folder, 'data.json'), mode='w', encoding='utf-8') as f:
        f.write(json.dumps(data_dto))
