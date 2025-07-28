# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import shutil
from distutils.core import setup
from setuptools import find_packages

PROJECT_FOLDER_NAME = "infy_search_service_tool"
ANGULAR_DIST_FOLDER = "../dist/browser"

# Copy the angular dist folder to the src folder
shutil.rmtree(f'src/{PROJECT_FOLDER_NAME}/www', ignore_errors=True)
shutil.copytree(ANGULAR_DIST_FOLDER, f'src/{PROJECT_FOLDER_NAME}/www',
                dirs_exist_ok=True)


setup(
    name="infy_search_service_tool",
    version="0.0.2",
    license="Apache License Version 2.0",
    author="Infosys Limited",
    author_email="",
    description="Run infy_search_service_tool locally",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    package_dir={'infy_search_service_tool': 'src/infy_search_service_tool'},
    packages=find_packages(where='src'),
    package_data={
            # Include all files in the www folder
            '': ['www/**/*']
    },
    entry_points={
        'console_scripts': [
            'infy_search_service_tool = infy_search_service_tool.launcher:start_server',
        ],
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "License :: Apache License Version 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
print('*******************************')
