import sys
import time

import Hydrogen
import os.path
import shutil
from pathlib import Path
import glob

from setuptools import setup, find_packages

readme_text = (Path(__file__).parent / 'README.md').read_text()

if not os.path.exists(r".\Release"):
    os.mkdir(r".\Release")


version_now = rf"{Hydrogen.version}.{Hydrogen.version_suffix}"
print(version_now)
time.sleep(3)
setup(
    name='HydrogenLib',
    version=version_now,
    author='SongzqInChina',
    author_email='idesong6@qq.com',
    description='A multi-functional module, but '
                'also the Hydrogen series of tools and modules of the front library',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    url='https://github.com/SongzqInChina/Hydrogen',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.12',
    install_requires=[
        'jsonpickle>=3.2.2',
        'psutil>=6.0.0'
    ],
)

print("Remove temp files")
print("Remove build ...")
shutil.rmtree('build')
print("Remove egg-info")
shutil.rmtree('HydrogenLib.egg-info')

print("Copy release file")

if "install" not in sys.argv:
    # get release whl file
    whl_file = glob.glob(r".\dist\*.whl")[0]
    shutil.copy(whl_file, rf".\Release")

    # get source code
    src_code_file = glob.glob(r".\dist\*.tar.gz")[0]
    src_code_file_name = rf"HydrogenLib-{version_now}.tar.gz"
    shutil.copy(src_code_file, rf".\Release\{src_code_file_name}")

print("Clean dist ...")
shutil.rmtree(r".\dist")

print("Finish.")


