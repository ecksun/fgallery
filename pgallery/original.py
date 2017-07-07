import sys

import os
import shutil
from os import path
from pgallery.config import config
from pgallery.image import Image


def create(image: Image, output_dir, relative_dir):
    destination = path.join(output_dir, 'files', relative_dir,
                            path.basename(image.original.path))

    if config.args.link_original == 'copy':
        shutil.copy(image.original.path, destination)
    elif config.args.link_original == 'symlink':
        symlink = path.relpath(image.original.path, path.dirname(destination))
        os.symlink(symlink, destination)
    elif config.args.link_original == 'hardlink':
        os.link(image.original.path, destination)
    else:
        print('Unsupported link mode %s' % config.args.link_original, file=sys.stderr)
