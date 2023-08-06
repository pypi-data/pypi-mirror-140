from setuptools import setup, find_packages
import codecs
import os




VERSION = '0.0.1'
DESCRIPTION = 'Calculating topsis'
# LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'/

# Setting up
setup(
    name="101903688",
    version=VERSION,
    author="Harindham",
    author_email="<harindamsharma18@gmail.com>",
    description=DESCRIPTION,
    # long_description_content_type="text/markdown",
    # long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas', 'numpy'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)