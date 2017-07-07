#!/usr/bin/python3
import json

import os
import shutil
from os import path
from pgallery.data_json import create_datadto, create_rootdto, create_thumbdto
from pgallery.image import Image, Dimension
from pgallery.original import create_original
from pgallery.scaledown import create_scaledown
from pgallery.thumb import create_thumb


def copy_template_files(destination):
    root_folder = path.join(path.dirname(path.abspath(__file__)), path.pardir)
    template_dir = path.join(root_folder, 'view')
    shutil.rmtree(destination)
    shutil.copytree(template_dir, destination)


def process_image(image: Image, input_dir, output_dir):
    relative_path = path.relpath(image.path, input_dir)
    relative_dir = path.dirname(relative_path)

    create_folders(output_dir, relative_dir)

    scaledown_size = create_scaledown(image, output_dir, relative_dir)
    thumb_size = create_thumb(image, output_dir, relative_dir)
    create_original(image, output_dir, relative_dir)

    return create_datadto(relative_path, scaledown_size, thumb_size, image.size, image.taken_date)


def create_folders(output_dir, target_dir):
    for directory in ('imgs', 'thumbs', 'files'):
        os.makedirs(path.join(output_dir, directory, target_dir), exist_ok=True)


def process_images(input_dir, output_dir, images: [Image]):
    datas = [process_image(image, input_dir, output_dir) for image in images]

    return create_rootdto(images=datas,
                          thumb=create_thumbdto(Dimension(100, 100),
                                                Dimension(200, 200)),
                          blur=Dimension(100, 200))


def process_and_save(images: [Image], input_dir, output_dir):
    data_dto = process_images(input_dir, output_dir, images)

    with open(path.join(output_dir, 'data.json'), mode='w', encoding='utf-8') as f:
        f.write(json.dumps(data_dto))
