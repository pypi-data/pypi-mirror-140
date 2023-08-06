# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libscreen",
    version="0.0.1",                        # Update this for every new version
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
        "Programming Language :: Python :: 3",    # projects. See all possible classifiers 
        "License :: OSI Approved :: MIT License", # in https://pypi.org/classifiers/
        "Operating System :: OS Independent",   
    ),
)
