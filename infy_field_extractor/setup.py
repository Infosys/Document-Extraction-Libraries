# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                 #
# ===============================================================================================================#

from distutils.core import setup
from setuptools import find_packages

METADATA = dict(
    name="infy_field_extractor",
    version="0.0.8",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="To extract the field such as checkboxes, radio buttons and text as key-value pairs from an image",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    # package_dir={'': 'src'},
    package_dir={
        'infy_field_extractor': 'src/infy_field_extractor',
        'infy_field_extractor/internal': 'src/infy_field_extractor/internal'},
    # packages=['checkbox_extractor_pkg'],
    packages=find_packages(where='src'),
    install_requires=[
        'opencv-python ==4.1.0.25',
        'numpy==1.18.1'
    ],
    extra_requires=[
        # The below libraries are required for the libraries own providers - tesseract and native pdf
        'infy_common_utils==0.0.4',
        'infy_ocr_parser==0.0.10'
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: Infosys Proprietary",
        "Operating System :: OS Independent",
    ],
    python_requires='==3.6.*',
)

if __name__ == '__main__':
    setup(**METADATA)
