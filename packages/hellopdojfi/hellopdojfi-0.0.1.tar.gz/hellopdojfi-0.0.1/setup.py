from setuptools import setup, find_packages
import codecs
import os

VERSION = "0.0.1"
DESCRIPTION = "Basic Hello package"

# Setting up
setup(
    name="hellopdojfi",
    version=VERSION,
    author="Kunal Gadhavi",
    author_email="<kunalgadhavi322@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=["python", "video", "stream", "video stream", "camera stream", "sockets"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
