# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
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
        _python_version_patch = sys.version.split(
            ' ', maxsplit=1)[0]  # E.g. XX.YY.ZZ
        _python_version_minor = ".".join(
            _python_version_patch.split('.')[:2])  # E.g XX.YY
        return _python_version_minor, _python_version_patch


class PipfileUtil:
    "Util class to parse Pipfile"
    @staticmethod
    def get_pip_file_path():
        '''Get pipfile path from CLI or return default'''
        return './Pipfile'

    @staticmethod
    def extract_python_version(pipfile_path):
        '''Get python version from Pipfile'''
        KEY_PYTHON_VERSION = "python_version"
        with open(pipfile_path, encoding="utf-8") as read_pipfile:
            value_list = list(line for line in (l.strip()
                                                for l in read_pipfile) if line.startswith(KEY_PYTHON_VERSION))
        _python_version_minor = value_list[0].split(
            '=')[1].strip().replace("\"", "")  # E.g XX.YY
        return _python_version_minor

    @staticmethod
    def extract_pkg_versions(pipfile_path):
        '''Get dependencies from Pipfile'''
        IDENTIFIER_GROUPS = "#[groups="
        with open(pipfile_path, encoding="utf-8") as read_pipfile:
            nonempty_line_list = list(line for line in (l.strip()
                                                        for l in read_pipfile) if line)
        line_list = []
        copy = False
        for line in nonempty_line_list:
            line = line.strip()
            if line == "[packages]":
                copy = True
                continue
            elif line.startswith("["):
                copy = False
                continue
            elif copy:
                if not line.startswith("#") and not IDENTIFIER_GROUPS in line:
                    line_list.append(line.rstrip())

        res = [x for x in line_list if '.whl' not in x]
        res = [x for x in res if 'docwblibs' not in x]

        pkg_line_list = [PipfileUtil.convert_to_pip_format(x) for x in res]
        return pkg_line_list

    @staticmethod
    def convert_to_pip_format(pipfile_format):
        '''Convert package name from Pipfile format to pip format'''
        new_format = pipfile_format
        if 'win32' not in new_format:
            new_format = new_format.replace(
                '=', '', 1).replace('"', '').replace(' ', '')
        else:
            new_format = new_format.replace(" ", "")
            new_format = new_format.replace('{version=', '')
            new_format = new_format.replace('}', '')
            new_format = new_format.replace("=", "", 1)
            new_format = new_format.replace(',sys_platform=', ';sys_platform')
            new_format = new_format.replace('"', '')
            new_format = new_format.replace(' ', '')
            new_format = new_format.replace("*", "")
        return new_format

    @staticmethod
    def extract_package_dir(root_dir_path):
        """Returns nested wheel file package dir to local dir pair as dict"""

        # Get all subfolders recursively
        my_list = [x[0] for x in os.walk(root_dir_path)]
        # Get relative path
        my_list = [os.path.relpath(x, root_dir_path) for x in my_list]
        # Remove any folder not inside src folder
        my_list = [x for x in my_list if x.startswith('src\\')]
        # Replace \ with /
        my_list = [x.replace('\\', '/') for x in my_list]
        # Remove autogenerated folders (ending with __)
        my_list = [x for x in my_list if not x.endswith('__')]

        # _ = [print(x) for x in my_list]

        my_dict = {x[len('src/'):]: x for x in my_list}
        return my_dict

    @staticmethod
    def extract_extras_versions(pipfile_path):
        '''Get extras dependencies from Pipfile which are installed only on demand'''
        IDENTIFIER_GROUPS = "#[groups="
        GROUP_ALL = "all"
        with open(pipfile_path, encoding="utf-8") as read_pipfile:
            nonempty_line_list = list(line for line in (l.strip()
                                                        for l in read_pipfile) if line)
        line_list = []
        extras_name = None
        for line in nonempty_line_list:
            line = line.strip()
            if line.startswith("#"):
                continue
            # E.g. #[groups=native,cloud]
            if IDENTIFIER_GROUPS in line:
                temp = line.split(IDENTIFIER_GROUPS)
                package_name, group_names = temp[0].strip(
                ), temp[1].strip().split(',')
                for group_name in group_names:
                    group_name = group_name.strip().replace(
                        ']', '').replace('[', '')
                    line_list.append([group_name, package_name])
                line_list.append([GROUP_ALL, package_name])

        res = [x for x in line_list if '.whl' not in x[1]]
        res = [x for x in res if 'docwblibs' not in x[1]]

        extras_name_list = list(dict.fromkeys([x[0] for x in res]))
        extras_dict = {}
        for extras_name in extras_name_list:
            res1 = [x[1] for x in res if x[0] == extras_name]
            extras_dict[extras_name] = [
                PipfileUtil.convert_to_pip_format(x) for x in res1]
        extra_all_list = []
        for v in extras_dict.values():
            extra_all_list += v
        return extras_dict


if __name__ == '__main__':

    pip_file_path = PipfileUtil().get_pip_file_path()
    print('Pipfile detected =>', pip_file_path)
    python_version_minor = PipfileUtil().extract_python_version(
        pip_file_path)  # E.g XX.YY
    print('Python version detected =>', python_version_minor)

    METADATA = dict(
        name="infy_dpp_core",
        version="0.0.3",
        license="Apache License Version 2.0",
        author="Infosys Limited",
        author_email="",
        description="DPP core processors",
        long_description="",
        long_description_content_type="text/markdown",
        url="",
        package_dir=PipfileUtil.extract_package_dir('.'),
        packages=find_packages(where='src'),
        package_data={
            # If any package contains *.ini files, include them:
            '': ['*.ini'],
        },
        install_requires=PipfileUtil().extract_pkg_versions(pip_file_path),
        extras_require=PipfileUtil().extract_extras_versions(pip_file_path),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3 :: Only",
            "License :: Apache License Version 2.0",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.8.0',

    )
    print('*******************************')
    setup(**METADATA)
