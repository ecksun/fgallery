import subprocess

import shutil
from pgallery.config import Config


def executable_exists(executable):
    return shutil.which(executable) is not None


def execute(cmd, config: Config):
    if config.verbose:
        print('Executing: %s %s' % (cmd[0], ' '.join(["'%s'" % arg for arg in cmd[1:]])))
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
