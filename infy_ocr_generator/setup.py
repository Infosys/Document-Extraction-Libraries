# ===============================================================================================================
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
# ===============================================================================================================#

from distutils.core import setup
from setuptools import find_packages

METADATA = dict(
    name="infy_ocr_generator",
    version="0.0.5",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="Generates OCR file(s) for the given documents",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    package_dir={'infy_ocr_generator': 'src/infy_ocr_generator',
                 'infy_ocr_generator/interface': 'src/infy_ocr_generator/interface',
                 'infy_ocr_generator/internal': 'src/infy_ocr_generator/internal',
                 'infy_ocr_generator/providers': 'src/infy_ocr_generator/providers',
                 },
    packages=find_packages(where='src'),
    install_requires=[
        'pytesseract ==0.3.2',
        'imageio ==2.9.0',
        "urllib3==1.26.7",
        'pywin32==301; sys_platform == "win32"',
        'comtypes==1.1.10; sys_platform == "win32"'
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
