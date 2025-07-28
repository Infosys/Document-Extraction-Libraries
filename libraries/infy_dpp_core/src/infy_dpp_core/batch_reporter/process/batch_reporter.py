# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
from jsonpath_ng import jsonpath, parse
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData


from infy_dpp_core.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "batch_reporter"

class BatchReporter(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        processor_config_data = config_data.get('BatchReporter', {})
        attributes_mapping = processor_config_data.get('attributes_mapping', {})
        summary_report_path = processor_config_data.get('summary_report_path','')

        extracted_values = {}
        for attribute, path in attributes_mapping.items():
            if path.startswith('document_data'):
                extracted_values[attribute] = self.get_nested_value(document_data, path[len('document_data.'):])
            elif path.startswith('context_data'):
                extracted_values[attribute] = self.get_nested_value(context_data, path[len('context_data.'):])
            elif path.startswith('$'):
                if path.startswith('$.document_data'):
                    extracted_values[attribute] = self.get_nested_value(document_data, '$' + path[len('$.document_data'):])
                elif path.startswith('$.context_data'):
                    extracted_values[attribute] = self.get_nested_value(context_data, '$' + path[len('$.context_data'):])
            else:
                extracted_values[attribute] = None

        if self.__file_sys_handler.exists(summary_report_path):
            existing_report_data_str = self.__file_sys_handler.read_file(summary_report_path)
            existing_report_data = json.loads(existing_report_data_str)
            if isinstance(existing_report_data, list):
                existing_report_data.append(extracted_values)
            else:
                existing_report_data = [existing_report_data, extracted_values]
            extracted_values_jsonstr = json.dumps(existing_report_data, ensure_ascii=False, indent=4)
        else:
            extracted_values_jsonstr = json.dumps([extracted_values], ensure_ascii=False, indent=4)
           
        self.__file_sys_handler.write_file(summary_report_path,extracted_values_jsonstr)
        
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "summary_report_path": summary_report_path
        }
        response_data.document_data = document_data
        response_data.context_data = context_data
        return response_data

    def get_nested_value(self, data, expression):
        if expression.startswith('$'):
            jsonpath_expr = parse(expression)
            data_dict = data.dict() if not isinstance(data, dict) else data
            match = jsonpath_expr.find(data_dict)
            if match:
                values = [m.value for m in match]
                return values if len(values) > 1 else values[0]
            else:
                self.__logger.error('No match found for query: %s', expression)
            return ""
        else:
            expression = expression.split('.')
            for key in expression:
                if isinstance(data, dict):
                    if '[' in key and ']' in key:
                        key, index = key.split('[')
                        index = int(index[:-1])
                        data = data.get(key, [])[index]
                    else:
                        data = data.get(key, {})
                elif isinstance(data, list):
                    try:
                        key = int(key)
                        data = data[key]
                    except (ValueError, IndexError):
                        self.__logger.error('No match found for query: %s', expression)
                        return None
                else:
                    try:
                        data = getattr(data, key, None)
                    except AttributeError:
                        self.__logger.error('No match found for query: %s', expression)
                        return None
                if data is None:
                    self.__logger.error('No match found for query: %s', expression)
                    return None
            return data