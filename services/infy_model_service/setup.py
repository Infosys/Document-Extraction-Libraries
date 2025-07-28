# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import setuptools

from distutils.core import setup
from setuptools import find_packages

setup(
    name="infy_model_service",
    version="0.0.2",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="Service for serving models.",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    package_dir={},
    packages=find_packages(where='src'),
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: Apache License Version 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
