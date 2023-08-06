from setuptools import setup, find_packages
import codecs
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Wayload",
    version="0.1.0",
    author="W4lk3r",
    author_email="w000alker@gmail.com",
    description="payload hide and extract module by W4lk3r",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['payload', 'payload bind', 'payload extract'],
    url="https://github.com/Walker-00/Wayload",
    project_urls={
        "Bug Tracker": "https://github.com/Walker-00/Wayload/issues",
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
