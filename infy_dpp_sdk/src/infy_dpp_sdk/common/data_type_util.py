# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Data Type Util class"""


class DataTypeUtil():
    """Util class for util methods to process common data types"""

    @classmethod
    def get_by_key_path(cls, data_dict: dict, key_path: str,
                        raise_error=False) -> any:
        """Get value from a dictionary using keypath"""
        return cls.__get_or_update_by_key_path(
            data_dict, key_path, is_update=False, raise_error=raise_error)

    @classmethod
    def update_by_key_path(cls, data_dict: dict, key_path: str,
                           value: any, raise_error=False) -> None:
        """Update value in a dictionary using keypath"""
        cls.__get_or_update_by_key_path(
            data_dict, key_path, is_update=True, value=value, raise_error=raise_error)

    @classmethod
    def get_all_key_paths(cls, data: any) -> list:
        """Get all key paths from a dictionary or list of dictionaries"""
        return cls.__traverse_dict(data)

    # ----------------Private Methods----------------
    @classmethod
    def __traverse_dict(cls, data, path='') -> list:
        key_path_list = []
        if isinstance(data, list):
            for idx, item in enumerate(data):
                key_path_list += cls.__traverse_dict(item, f"{path}[{idx}]")
        elif isinstance(data, dict):
            for key, value in data.items():
                _path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    key_path_list += cls.__traverse_dict(value, _path)
                elif isinstance(value, list):
                    key_path_list += cls.__traverse_dict(value, _path)
                else:
                    # print(f"{_path} = {value}")
                    key_path_list += [[_path, value]]
        else:
            # print(f"*{path} = {data}")
            key_path_list += [[path, data]]

        return key_path_list

    @classmethod
    def __get_or_update_by_key_path(cls, data_dict: dict, key_path: str,
                                    is_update: bool = False, value: str = None,
                                    raise_error=False) -> any:
        """Get/update value from a dictionary using keypath"""
        key_path_token_list = key_path.split(".")
        _data_dict = data_dict
        key_path_token_found_list = []
        for key_path_token in key_path_token_list[:-1]:
            index = None
            _key_path_token = key_path_token
            if _key_path_token.endswith("]"):
                _key_path_token, index = _key_path_token.split("[")
                index = int(index.replace("]", ""))
            if _key_path_token in _data_dict:
                _data_dict = _data_dict[_key_path_token]
                if index is not None:
                    _data_dict = _data_dict[index]
                key_path_token_found_list.append(key_path_token)
                if not _data_dict:
                    break
        if _data_dict:
            key_path_token = key_path_token_list[-1]
            if is_update:
                _data_dict[key_path_token] = value
                _data_dict = data_dict
            else:
                _data_dict = _data_dict[key_path_token]
            key_path_token_found_list.append(key_path_token)

        found_key_path = ".".join(key_path_token_found_list)
        if not key_path == found_key_path:
            if raise_error:
                message = f"Keypath not found!: Requested keypath = '{key_path}' "
                message = f"| Found keypath: '{found_key_path}'"
                raise ValueError(message)
            return None
        # For update mode, value is updated directly in input data_dict itself
        return None if is_update else _data_dict
