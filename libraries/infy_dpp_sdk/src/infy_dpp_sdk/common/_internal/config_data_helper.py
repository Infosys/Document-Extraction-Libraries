# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Config Data Helper class"""
import os
import re
import copy
import logging
from .data_type_util import DataTypeUtil


class ConfigDataHelper():
    """Class for Config Data Helper"""

    __VAR_TYPE_LOCAL = "Local variable"
    __VAR_TYPE_OS_ENV = "OS env variable"
    __PREFIX_OS_ENV_VARIABLE = "ENV:"

    def __init__(self, logger: logging.Logger = None):
        self.__logger = logger

    def generate_default_deployment_config(self, input_config_data: dict) -> dict:
        """Generate a default deployment config data from input config data"""
        processors_dict = {}
        processor_list = []
        level_1_list = input_config_data.get('processor_list', [])
        for item in level_1_list:
            if item.get('processor_list'):
                processor_list.extend(item.get('processor_list'))
            else:
                processor_list.append(item)
        for processor in processor_list:
            processor_name = processor.get('processor_name')
            processors_dict[processor_name] = {
                'enabled': processor.get('enabled'),
                "args": {
                    "request_file_path": "${SYS_CONTROLLER_REQ_FILE_PATH}"
                },
                "output": {
                    "variables": {
                        "SYS_CONTROLLER_RES_FILE_PATH": "response_file_path"
                    }
                }
            }
        deployment_config_dict = {
            "variables": {},
            "processors": processors_dict
        }
        return deployment_config_dict

    def validate_dpp_deployment_config(self, config_data) -> list:
        """Validate DPP deployment config file"""
        validation_messages = []
        VALIDATE_DEPLOYMENT_CONFIG_PATH_LIST = [
            'processor_home_dir', 'cli_controller_dir', 'venv_script_dir']
        key_missing_dict, invalid_path_dict = {}, {}
        for key, value in config_data.get('processors', {}).items():
            if not value.get('enabled'):
                continue
            for x in VALIDATE_DEPLOYMENT_CONFIG_PATH_LIST:
                if not value.get(x):
                    self.__add_or_update_dict(key_missing_dict, key, x)
                elif not os.path.exists(value.get(x)):
                    self.__add_or_update_dict(invalid_path_dict, key, x)
        if key_missing_dict:
            message = f"INVALID DEPLOYMENT CONFIG FILE: key is missing -> {key_missing_dict}"
            self.__logger.error(message)
            validation_messages.append(message)
        if invalid_path_dict:
            message = f"INVALID DEPLOYMENT CONFIG FILE: path is not valid -> {invalid_path_dict}"
            self.__logger.error(message)
            validation_messages.append(message)
        return validation_messages

    def validate_dpp_input_config(self, input_config_data, deployment_config_data) -> list:
        """Validate DPP input config file"""
        validation_messages = []
        enabled_processor_list = [k for k, v in deployment_config_data.get(
            'processors', {}).items() if v.get('enabled')]
        not_enabled_processors_list = []
        for x in input_config_data.get('processor_list', []):
            if not x.get('enabled'):
                continue
            if x.get('processor_name') not in enabled_processor_list:
                not_enabled_processors_list.append(x.get('processor_name'))
        if not_enabled_processors_list:
            message = "INVALID INPUT CONFIG FILE: "
            message += f"processor(s) are not enabled in deployment config -> {not_enabled_processors_list}"
            self.__logger.error(message)
            validation_messages.append(message)
        return validation_messages

    def do_interpolation(self, config_data):
        """Interpolation of variables in config data"""
        KEY_NAME_VARIABLES = 'variables'
        variables_dict = config_data.get(KEY_NAME_VARIABLES, {})
        # Interpolate variables, local first and then OS environment variables
        for var_name, var_value in variables_dict.items():
            other_var_name_type_list = self.__extract_variable_names(var_value)
            if other_var_name_type_list:
                other_var_name_value_dict = self.__fetch_variable_values(
                    other_var_name_type_list, variables_dict)
                new_value = self.__substitute_variable_values(
                    var_value, other_var_name_value_dict)
                new_value_source = [{x: y['source']}
                                    for x, y in other_var_name_value_dict.items()]
                if var_value != new_value:
                    variables_dict[var_name] = new_value
                    message = f"DPP variable updated | Name: {var_name}"
                    message += f" | Source: {new_value_source} | Val length: {len(new_value)} char(s)"
                    self.__logger.info(message)

        config_data_1 = copy.deepcopy(config_data)
        key_path_and_value_list = DataTypeUtil.get_all_key_paths(config_data_1)
        for key_path_and_value in key_path_and_value_list:
            key_path = key_path_and_value[0]
            if key_path.split('.')[0] == KEY_NAME_VARIABLES:
                continue
            key_path_value = key_path_and_value[1]
            other_var_name_type_list = self.__extract_variable_names(
                key_path_value)
            if other_var_name_type_list:
                other_var_name_value_dict = self.__fetch_variable_values(
                    other_var_name_type_list, variables_dict)
                new_value = self.__substitute_variable_values(
                    key_path_value, other_var_name_value_dict)
                new_value_source = [{x: y['source']}
                                    for x, y in other_var_name_value_dict.items()]
                if key_path_value != new_value:
                    DataTypeUtil.update_by_key_path(
                        config_data_1, key_path, new_value)
                    message = f"DPP variable updated | Name: {key_path}"
                    message += f" | Source: {new_value_source} | Val length: {len(new_value)} char(s)"
                    self.__logger.info(message)
        return config_data_1

    # ----------------- Private methods ----------------- #

    def __add_or_update_dict(self, d, k, v):
        if k in d:
            d[k].append(v)
        else:
            d[k] = [v]
        return d

    def __extract_variable_names(self, text: str) -> list:
        _text = text if isinstance(text, str) else str(text)
        PATTERN_LOCAL_VARIABLE = r'\$\{(\w+)\}'
        PATTERN_ENV_VARIABLE = r'\$\{ENV:(\w+)\}'
        matches = []
        for pattern, label in zip([PATTERN_LOCAL_VARIABLE, PATTERN_ENV_VARIABLE],
                                  [self.__VAR_TYPE_LOCAL, self.__VAR_TYPE_OS_ENV]):
            _matches = re.findall(pattern, _text)
            if pattern == PATTERN_ENV_VARIABLE:
                # Add ENV as prefix to the matches
                _matches = [self.__PREFIX_OS_ENV_VARIABLE +
                            x for x in _matches if x]
            _matches = [[x, label] for x in _matches]
            matches.extend(_matches)
        return matches

    def __fetch_variable_values(self, var_name_type_list: list, var_value_dict: dict = None):
        """Fetch variable values from local variables and OS environment variables. 
        Local variables take precedence over OS environment variables.
        To force fetching from OS environment variables, use format "${ENV:myvar}" where
        myvar is your variable name.
        """
        var_name_value_dict = {}
        for var_name, var_type in var_name_type_list:
            if var_type == self.__VAR_TYPE_OS_ENV:
                _var_name = var_name.replace(self.__PREFIX_OS_ENV_VARIABLE, '')
                value = os.environ.get(_var_name)
                source = self.__VAR_TYPE_OS_ENV
            elif var_value_dict and var_name in var_value_dict:
                value = var_value_dict.get(var_name)
                source = self.__VAR_TYPE_LOCAL
            elif var_name in os.environ:
                value = os.environ.get(var_name)
                source = self.__VAR_TYPE_OS_ENV
            else:
                value = None
                source = None
            var_name_value_dict[var_name] = {'value': value, 'source': source}
        return var_name_value_dict

    def __substitute_variable_values(self, text: str, var_value_dict: dict) -> str:
        updated_text = text
        for var_name, value_dict in var_value_dict.items():
            if not value_dict['source']:
                continue
            value = value_dict['value']
            value = str(value) if not isinstance(value, str) else value
            updated_text = updated_text.replace('${' + var_name + '}', value)
        return updated_text
