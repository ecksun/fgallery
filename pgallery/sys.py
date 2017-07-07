import subprocess


def execute(cmd):
    print(cmd)
    return subprocess.run(cmd, stdout=subprocess.PIPE, check=True)