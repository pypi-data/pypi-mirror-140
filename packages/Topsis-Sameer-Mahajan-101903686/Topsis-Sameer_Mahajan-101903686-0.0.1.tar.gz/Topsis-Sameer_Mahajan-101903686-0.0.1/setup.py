#Name: Sameer Mahajan
#Batch: Coe26
#Roll no.:101903686
# Setting up

from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Calculate Topsis Score'

setup(
    name="Topsis-Sameer_Mahajan-101903686",
    version=VERSION,
    author="Sameer Mahajan",
    author_email="<mahajansameer19@gmail.com>",
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