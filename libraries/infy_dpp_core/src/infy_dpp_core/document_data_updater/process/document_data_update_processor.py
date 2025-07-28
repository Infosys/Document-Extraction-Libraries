# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List

import infy_dpp_sdk
from infy_dpp_sdk.data import *
from jsonpath_ng import parse

from infy_dpp_core.document_data_updater.common.common_util import CommonUtil
from infy_dpp_core.document_data_updater.rules.rule_data_base_class import \
    RuleDataBaseClass


class DocumentDataUpdateProcessor(infy_dpp_sdk.interface.IProcessor):
    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        org_document_data_json = {'document_data': document_data.dict(), 'context_data': context_data,
                                  'message_data': []}
        updated_json = self.__update_json(
            org_document_data_json, config_data.get('DocumentDataUpdater', {}).get('config_data', []))
        new_document_data = infy_dpp_sdk.data.DocumentData(
            **updated_json.get('document_data', {}))
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=new_document_data, context_data=updated_json.get(
                'context_data'),
            message_data=infy_dpp_sdk.data.MessageData(messages=updated_json.get('message_data', [])))
        return response_data

    def __update_json(self, json_data, config_data_list):
        for config_data in config_data_list:
            if not config_data.get('enabled'):
                continue
            json_path = config_data.get('json_path')
            jsonpath_expr = parse(json_path)
            matches = jsonpath_expr.find(json_data)
            if not matches:
                self.__logger.info(
                    f"json_path not found in document_data.json - {json_path}")
                continue
            rule_name = config_data.get('replace_value_with_rule_name')
            if rule_name:
                rule_class = CommonUtil.get_rule_class_instance(rule_name)
                rule_instance: RuleDataBaseClass = rule_class()
            for match_data in matches:
                json_key = config_data.get('json_key')
                if config_data.get('replace_key_enabled'):
                    target_node = match_data.value
                    target_node[config_data.get(
                        'replace_with_key')] = target_node.pop(json_key)
                if config_data.get('replace_value_enabled'):
                    match_data.value[json_key] = config_data.get(
                        'replace_with_value')
                if rule_name:
                    match_data.value[json_key] = rule_instance.do_process(
                        match_data.value[json_key])
        return json_data
