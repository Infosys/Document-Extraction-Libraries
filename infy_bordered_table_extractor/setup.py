# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                   #
# ===============================================================================================================#

from distutils.core import setup
from setuptools import find_packages

METADATA = dict(
    name="infy_bordered_table_extractor",
    version="0.0.7",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="To extract field values from bordered table in an image and convert to excel",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    package_dir={'infy_bordered_table_extractor': 'src/infy_bordered_table_extractor',
                 'infy_bordered_table_extractor/internal': 'src/infy_bordered_table_extractor/internal',
                 'infy_bordered_table_extractor/providers': 'src/infy_bordered_table_extractor/providers',
                 'infy_bordered_table_extractor/interface': 'src/infy_bordered_table_extractor/interface'},
    packages=find_packages(where='src'),
    install_requires=[
        'opencv-python ==4.5.5.64',
        'numpy>=1.13.3,<=1.23.0',
        'bs4==0.0.1',
        'lxml==4.6.5',
        'pandas>=1.1.5,<=1.4.3',
        'imageio==2.9.0',
        "Jinja2==3.0.3",
        "openpyxl==3.0.5",
        'scikit-learn>=0.24.2,<=1.1.1'
    ],
    extra_requires=[
        'pytesseract==0.3.2',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "License :: Apache License Version 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6.2',
)

if __name__ == '__main__':
    setup(**METADATA)
