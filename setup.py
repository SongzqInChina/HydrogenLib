from setuptools import setup, find_packages
from pathlib import Path

readme_text = (Path(__file__).parent / 'README.md').read_text()

setup(
    name='HydrogenLib',
    version='0.1.0',
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
        'psutil>=6.0.0',
    ],
)
