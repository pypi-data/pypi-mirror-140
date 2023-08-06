#!/usr/bin/env python
#-*- coding:utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onez",
    version="0.0.37",
    author="99onez",
    author_email="nikkyyang2289@qq.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords = ("pip", "testpypi"),
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
'''
from setuptools import setup, find_packages

setup(
    name = "onez",
    version = "0.0.33",
    keywords = ("pip", "testpypi"),
    description = "test pip module",
    long_description = "test how to define pip module and upload to pypi",
    license = "MIT",

    url = "http://127.0.0.1:5000/",
    #url = "https://99onez.com",          # your module home page, such as
    author = "99onez",                         # your name
    author_email = "99onez@qq.com",    # your email

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)



cd..
python setup.py sdist      
python setup.py bdist_egg
cd dist
pip install onez-0.0.313.tar.gz





'''