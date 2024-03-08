# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

'''Module for generating wheel file based on python version and Pipfile'''
import sys
import site
import os
from distutils.core import setup
from setuptools import find_packages

print('CLI Args =', sys.argv)


class PythonEnvUtil:
    "Util class for python functions"
    @staticmethod
    def get_env_python_info():
        '''Get python details from current environment'''
        print('Python executable =>', os.path.dirname(sys.executable))
        print('Python site packages =>', site.getsitepackages())

    @staticmethod
    def get_env_python_version():
        '''Get python version from current environment'''
        _python_version_patch = sys.version.split(' ')[0]  # E.g. XX.YY.ZZ
        _python_version_minor = ".".join(
            _python_version_patch.split('.')[:2])  # E.g XX.YY
        return _python_version_minor, _python_version_patch


class PipfileUtil:
    "Util class to parse Pipfile"
    @staticmethod
    def get_pip_file_path():
        '''Get pipfile path from CLI or return default'''
        return './Pipfile'
        script_file_path = os.path.abspath(sys.argv[0])
        script_dir_path = os.path.dirname(
            script_file_path) if os.path.exists(script_file_path) else '.'
        _python_version_minor, _ = PythonEnvUtil.get_env_python_version()
        # _pipfile_path = './Pipfile'
        _pipfile_path = f"{script_dir_path}/Pipfile_v{_python_version_minor.replace('.','')}"
        KEY_PIPFILE_PATH = "--pipfilepath"
        if KEY_PIPFILE_PATH in sys.argv:
            value_index = sys.argv.index(KEY_PIPFILE_PATH)+1
            if value_index < len(sys.argv):
                _pipfile_path = sys.argv[value_index]
                print('Found pipfile path in CLI args =>', _pipfile_path)
                # Remove the args after reading to prevent setup() error
                sys.argv.pop(value_index-1)
                sys.argv.pop(value_index-1)
        return _pipfile_path

    @staticmethod
    def extract_python_version(pipfile_path):
        '''Get python version from Pipfile'''
        KEY_PYTHON_VERSION = "python_version"
        with open(pipfile_path) as read_pipfile:
            value_list = list(line for line in (l.strip()
                                                for l in read_pipfile) if line.startswith(KEY_PYTHON_VERSION))
        _python_version_minor = value_list[0].split(
            '=')[1].strip().replace("\"", "")  # E.g XX.YY
        return _python_version_minor

    @staticmethod
    def extract_pkg_versions(pipfile_path):
        '''Get dependencies from Pipfile'''
        with open(pipfile_path) as read_pipfile:
            nonempty_line_list = list(line for line in (l.strip()
                                                        for l in read_pipfile) if line)
        line_list = []
        copy = False
        for line in nonempty_line_list:
            if line.strip() == "[packages]":
                copy = True
                continue
            elif line.strip() == "[requires]":
                copy = False
                continue
            elif copy:
                if not line.startswith("#"):
                    line_list.append(line.rstrip())

        res = [x for x in line_list if '.whl' not in x]
        res = [x for x in res if 'docwblibs' not in x]

        pkg_line_list = [x.replace('=', '', 1).replace('"', '') if 'win32' not in x
                         else x.replace(" ", "").replace('{version=', '')
                         .replace('}', '').replace("=", "", 1)
                         .replace(',sys_platform=', ' ;sys_platform')
                         .replace('"', '')
                         for x in res]
        return pkg_line_list


if __name__ == '__main__':

    pip_file_path = PipfileUtil().get_pip_file_path()
    print('Pipfile detected =>', pip_file_path)
    python_version_minor = PipfileUtil().extract_python_version(
        pip_file_path)  # E.g XX.YY
    print('Python version detected =>', python_version_minor)

    METADATA = dict(
        name="infy_field_extractor",
        version="0.0.12",
        license="Apache License Version 2.0",
        author="Infosys Limited",
        author_email="",
        description="To extract the field such as checkboxes, radio buttons and text as key-value pairs from an image",
        long_description="",
        long_description_content_type="text/markdown",
        url="",
        package_dir={
            'infy_field_extractor': 'src/infy_field_extractor',
            'infy_field_extractor/internal': 'src/infy_field_extractor/internal'},
        packages=find_packages(where='src'),
        install_requires=PipfileUtil().extract_pkg_versions(pip_file_path),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3 :: Only",
            "License :: Apache License Version 2.0",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6.2',
    )
    print('*******************************')
    setup(**METADATA)
