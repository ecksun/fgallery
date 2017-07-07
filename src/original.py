import shutil
from os import path
from src.fgallery import Image, args


def create_original(image: Image, relative_dir):
    shutil.copy(image.path, path.join(args.output, 'files', relative_dir))