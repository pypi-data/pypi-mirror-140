from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.7'
DESCRIPTION = 'Various scripts from justcow.'

# Setting up
setup(
    name="megacrazyscripts",
    version=VERSION,
    author="JustCow",
    author_email="<justcow@pm.me>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['ffmpeg-python', 'pedalboard', 'youtube_dl', 'pillow'],
    keywords=['python', 'video', 'audio', 'youtubedl', 'justcow'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)