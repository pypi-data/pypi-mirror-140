#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


def read_requirements(filename):
    return [req.strip() for req in open(filename)]


setup(
    name="transkribus-client",
    version=open("VERSION").read().strip(),
    author="Teklia <contact@teklia.com>",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    package_data={
        "": ["README.md", "LICENSE"],
    },
    install_requires=read_requirements("requirements.txt"),
    python_requires=">=3.6",
    license="MIT",
    description="Unofficial API client for the Transkribus project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="api client transkribus",
    url="https://gitlab.com/arkindex/transkribus",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Text Processing :: Linguistic",
    ],
)
