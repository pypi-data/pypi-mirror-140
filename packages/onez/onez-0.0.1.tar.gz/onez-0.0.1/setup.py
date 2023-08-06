#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "onez",
    version = "0.0.1",
    keywords = ("pip", "testpypi"),
    description = "test pip module",
    long_description = "test how to define pip module and upload to pypi",
    license = "MIT",

    url = "https://99onez.com",          # your module home page, such as
    author = "99onez",                         # your name
    author_email = "99onez@qq.com",    # your email

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)