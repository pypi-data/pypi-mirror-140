#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

VERSION = "0.10.2"

setup(
    author="Ricardo",
    author_email="gzsushixuan@corp.netease.com",
    description="SDK of alpha@gdc group.",
    name="alphabases",
    packages=find_packages(),
    zip_safe=False,
    version=VERSION,
)


