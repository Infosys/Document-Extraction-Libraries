# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Data Type Util class"""


class DataTypeUtil():
    """Util class for util methods to process common data types"""

    @classmethod
    def get_by_key_path(cls, data_dict: dict, key_path: str, raise_error=False):
        """Get value from a dictionary using keypath"""
        key_path_token_list = key_path.split(".")
        _data_dict = data_dict
        key_path_token_found_list = []
        for key_path_token in key_path_token_list:
            if key_path_token in _data_dict:
                key_path_token_found_list.append(key_path_token)
                _data_dict = _data_dict[key_path_token]
                if not _data_dict:
                    break
        found_key_path = ".".join(key_path_token_found_list)
        if not key_path == found_key_path:
            if raise_error:
                message = f"Keypath not found!: Requested keypath = '{key_path}' | Found keypath: '{found_key_path}'"
                raise ValueError(message)
            return None
        return _data_dict
