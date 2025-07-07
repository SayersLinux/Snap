#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="snap-osint",
    version="1.0.0",
    author="SayersLinux",
    author_email="SayerLinux@gmail.com",
    description="Social Network Analysis and Profiling Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SayersLinux/snap",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
        "Topic :: Internet",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "snap=snap:main",
        ],
    },
)