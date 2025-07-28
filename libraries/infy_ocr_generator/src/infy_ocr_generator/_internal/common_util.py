# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class CommonUtil:
    """Common util class"""
    @classmethod
    def get_invalid_keys(cls, truth_dict, test_dict):
        """Compare two dictionary objects and return invalid keys by using one of them as reference

        Args:
            truth_dict (dict): The object containing all valid keys
            test_dict (dict): The object to evaluate for presence of invalid keys

        Returns:
            list: The list of invalid keys
        """
        truth_keys = cls.__get_all_keys_recursively(None, truth_dict)
        # print(truth_keys)
        test_keys = cls.__get_all_keys_recursively(None, test_dict)
        # print(test_keys)
        return list(set(test_keys)-set(truth_keys))

    @classmethod
    def __get_all_keys_recursively(cls, parent_key, dict_obj):
        all_keys = []
        for k, val in dict_obj.items():
            key = k if parent_key is None or len(
                parent_key) == 0 else f"{parent_key}->{k}"
            if not key in all_keys:
                all_keys.append(key)
            if isinstance(val, dict):
                all_keys += cls.__get_all_keys_recursively(key, val)
        return all_keys
