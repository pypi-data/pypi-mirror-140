from setuptools import setup, find_packages
import codecs
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Wlyrics-W4lk3r",
    version="0.1.21",
    author="W4lk3r",
    author_email="w000alker@gmail.com",
    description="song lyrics pip by W4lk3r",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['song lyrics', 'music lyrics', 'lyrics'],
    url="https://github.com/Walker-00/Wlyrics",
    project_urls={
        "Bug Tracker": "https://github.com/Walker-00/Wlyrics/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)
