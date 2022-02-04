# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from distutils.core import setup
from setuptools import find_packages

METADATA = dict(
    name="infy_ocr_parser",
    version="0.0.10",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="OCR Parser to search relative bbox of anchor text.",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    package_dir={'infy_ocr_parser': 'src/infy_ocr_parser',
                 'infy_ocr_parser/internal': 'src/infy_ocr_parser/internal',
                 'infy_ocr_parser/interface': 'src/infy_ocr_parser/interface',
                 'infy_ocr_parser/providers': 'src/infy_ocr_parser/providers'
                 },
    packages=find_packages(where='src'),
    install_requires=[
        'bs4==0.0.1',
        'lxml ==4.6.2'
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
