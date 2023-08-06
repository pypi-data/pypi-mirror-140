# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libscreen",
    version="69.0.8",                        # Update this for every new version
    author="Your name",
    author_email="your@email.com",
    description="long description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[                      # Add project dependencies here
    ],
    url="https://github.com/your/github/project",
    packages=setuptools.find_packages(),
    classifiers=(                                 # Classifiers help people find your
        # projects. See all possible classifiers
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # in https://pypi.org/classifiers/
        "Operating System :: OS Independent",
    ),
)
