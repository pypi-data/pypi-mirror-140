import os
import subprocess

def check_dependencies():
    cuda_lib = '/usr/local/cuda/targets/x86_64-linux/lib/libcudart.so.11.0'

    if os.path.exists(cuda_lib) is False:
        raise RuntimeError("Cuda 11.0 required.")


def update_lib_path():
    lib_path = os.path.abspath(os.path.dirname(__file__))
    subprocess.check_call(['patchelf', '--set-rpath', lib_path, os.path.join(lib_path, './ct_algos.so')])

check_dependencies()
update_lib_path()

from . import ct_algos
assert (ct_algos is not None)

