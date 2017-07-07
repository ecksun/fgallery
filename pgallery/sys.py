import subprocess

import shutil


def executable_exists(executable):
    return shutil.which(executable) is not None


def execute(cmd):
    print(cmd)
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
