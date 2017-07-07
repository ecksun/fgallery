import shutil
from os import path
from pgallery.image import Image


def create_original(image: Image, output_folder, relative_dir):
    shutil.copy(image.path, path.join(output_folder, 'files', relative_dir))
