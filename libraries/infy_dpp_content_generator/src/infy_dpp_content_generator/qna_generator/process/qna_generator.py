# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import importlib
import json
import re
import copy
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData
import infy_content_generator
from jsonpath_ng import parse


PROCESSEOR_CONTEXT_DATA_NAME = "qna_generator"


class QnaGenerator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:

        processor_response_data = ProcessorResponseData()
        qna_generator_config_data = config_data.get('QnaGenerator', {})

        qna_data_list = []

        for technique in qna_generator_config_data.get('techniques', []):
            if technique.get('enabled'):
                qna_strategy_name = technique.get("qna_strategy_name")
                llm_providers = technique.get("llm_providers")
                llm_providers_dict = copy.deepcopy(llm_providers)

                content_class = technique.get('content_class')
                content_type = technique.get('content_type')
                page_pattern_list = technique.get('page_num', [])
                technique_name = technique.get('name')
                min_content_char_length = technique.get(
                    'min_content_char_length', None)

                custom_meta_data = {}
                # Retrieve the custom metadata from the chunked file metadata list
                chunked_file_meta_data_list = context_data.get(
                    'metadata_extractor_custom_document', {}).get('chunked_file_meta_data_list')
                if chunked_file_meta_data_list:
                    meta_data_file_content_json = json.loads(self.__file_sys_handler.read_file(
                        chunked_file_meta_data_list[0]))
                    custom_meta_data = meta_data_file_content_json.get(
                        "custom_metadata")
                # End of custom metadata retrieval from chunked file metadata list
                self.__logger.debug(
                    "custom_meta_data::%s", custom_meta_data)

                # QNA STRATEGY OBJECT CREATION
                if isinstance(qna_strategy_name, str) and qna_strategy_name.startswith("$"):
                    jsonpath_expr = parse(qna_strategy_name)
                    qna_strategy_dict = [match.value for match in jsonpath_expr.find(
                        qna_generator_config_data)][0]
                    if qna_strategy_dict.get("enabled"):
                        qna_strategy_provider_config_data = qna_strategy_dict.get(
                            "qna_strategy_provider_config_data")
                        qna_strategy_provider = qna_strategy_dict.get(
                            "qna_strategy_provider")

                        qna_strategy_provider_config_data_cls = qna_strategy_provider_config_data.get(
                            "class")
                        qna_strategy_config_data_cpy = copy.deepcopy(
                            qna_strategy_provider_config_data)
                        que_type = qna_strategy_config_data_cpy.get(
                            "properties").get("que_type")
                        if isinstance(que_type, str) and que_type.startswith("$"):
                            jsonpath_expr = parse(que_type)
                            qna_strategy_config_data_cpy["properties"]["que_type"] = [
                                match.value for match in jsonpath_expr.find(
                                    qna_generator_config_data)][0]
                        # Converting the que_type dictionary to StrategyConfigData dictionary
                        que_type_dict = {}
                        for q_type_key, val in qna_strategy_config_data_cpy["properties"]["que_type"].items():
                            que_type_dict[q_type_key] = {'count': val}
                        qna_strategy_config_data_cpy["properties"]["que_type"] = que_type_dict

                        # Create an object of the Provider Config Data class
                        module_name, provider_config_data_cls_name = qna_strategy_provider_config_data_cls.rsplit(
                            '.', 1)
                        module = importlib.import_module(module_name)
                        qna_strategy_provider_config_data_cls_obj = getattr(
                            module, provider_config_data_cls_name)(**qna_strategy_config_data_cpy.get(
                                "properties"))

                        # Create an object of the Provider class
                        qna_strategy_provider_cls = qna_strategy_provider.get(
                            "class")
                        module_name, qna_strategy_provider_cls_name = qna_strategy_provider_cls.rsplit(
                            '.', 1)
                        module = importlib.import_module(module_name)
                        qna_strategy_provider_cls_obj = getattr(
                            module, qna_strategy_provider_cls_name)(qna_strategy_provider_config_data_cls_obj)
                        # IF PROMPT FILE PATH IS NOT NONE THEN SET PROMPT FILE PATH
                        # Sets prompt template dict if file path given, reads the content and set the template
                        prompt_files_path = qna_strategy_provider.get(
                            "properties").get("prompt_files_path")
                        if prompt_files_path:
                            PROMPT_TEMPLATE_DICT = qna_strategy_provider_cls_obj.get_prompt_template()
                            for prompt_file_key, prompt_file_value in prompt_files_path.items():
                                if prompt_file_value is not None:
                                    PROMPT_TEMPLATE_DICT[prompt_file_key] = self.__file_sys_handler.read_file(
                                        prompt_file_value)

                            qna_strategy_provider_cls_obj.set_prompt_template(
                                PROMPT_TEMPLATE_DICT)

                # LLM PROVIDERs OBJECT's DICTONARY CREATION
                for llm_provider_key, llm_provider_value in llm_providers_dict.items():
                    if isinstance(llm_provider_value, str) and llm_provider_value.startswith("$"):
                        jsonpath_expr = parse(llm_provider_value)
                        llm_dict = [
                            match.value for match in jsonpath_expr.find(qna_generator_config_data)][0]
                        if llm_dict.get("enabled"):
                            llm_config_data = llm_dict.get("configuration")
                            llm_provider_config_data_class = llm_dict.get(
                                "llm_provider_config_data_class")
                            llm_provider_class = llm_dict.get(
                                "llm_provider_class")
                            # Split the class name into module name and class name
                            module_name, provider_config_data_class_name = llm_provider_config_data_class.rsplit(
                                '.', 1)
                            # Import the module
                            module = importlib.import_module(module_name)
                            # Create an object of the Provider Config Data class
                            llm_provider_config_data_class_obj = getattr(
                                module, provider_config_data_class_name)(**llm_config_data)

                            # Create an object of the Provider class
                            module_name, provider_class_name = llm_provider_class.rsplit(
                                '.', 1)
                            module = importlib.import_module(module_name)
                            llm_provider_class_obj = getattr(module, provider_class_name)(
                                llm_provider_config_data_class_obj)

                            llm_providers_dict[llm_provider_key] = llm_provider_class_obj

                # SET LLM PROVIDERS
                qna_strategy_provider_cls_obj.set_llm_provider(
                    llm_providers_dict)

                qna_generator_obj = infy_content_generator.generator.QnaGenerator(
                    qna_strategy_provider_cls_obj)

                total_pages = 100000
                raw_data_dict = document_data.raw_data.dict()
                segment_data_list = raw_data_dict.get('segment_data')
                extracted_page_list = set([i['page']
                                          for i in segment_data_list])
                pages_list = self.lookp_up_page(total_pages, page_pattern_list)
                pages_list = list(set(pages_list).intersection(
                    set(extracted_page_list)))

                CONTEXT = ""
                if content_class == 'segment':
                    for segment_data in context_data.get('segment_sequencer').get('segment_data'):
                        for segment in segment_data.get('segments'):
                            segment_page_list = []
                            if content_type:
                                if segment.get("content_type") == content_type:
                                    page_no = segment.get("page")
                                    if page_no in pages_list:
                                        CONTEXT = segment.get("content")

                            else:
                                page_no = segment.get("page")
                                if page_no in pages_list:
                                    CONTEXT = segment.get("content")

                            segment_content_type = segment.get("content_type")
                            content_class_id = segment.get("segment_id")
                            segment_seq_no = segment.get("sequence")
                            if min_content_char_length:
                                if len(CONTEXT) <= min_content_char_length:
                                    continue
                            segment_page_list.append(page_no)
                            # Function Call to generate qna segment wise
                            qna_response_data = qna_generator_obj.generate_qna(
                                [CONTEXT], custom_meta_data)
                            qna_data = json.loads(json.dumps(
                                qna_response_data, default=lambda o: o.__dict__, indent=4))

                            for qna_dict in qna_data.get("qna_data_list"):
                                qna_dict["content_class"] = content_class
                                qna_dict["content_type"] = segment_content_type
                                qna_dict["content_class_id"] = content_class_id
                                qna_dict["document_name"] = document_data.metadata.standard_data.filename.value
                                qna_dict["page_no"] = segment_page_list
                                qna_dict["doc_id"] = document_data.document_id
                                qna_dict["technique_name"] = technique_name
                                qna_dict["llm_name"] = [llm_namespace.rsplit(
                                    '.', 1)[-1] for llm_namespace in llm_providers.values()]
                                qna_dict["qna_strategy_name"] = qna_strategy_name.rsplit(
                                    '.', 2)[-1]
                                qna_dict["sequence_no"] = segment_seq_no
                            qna_data_list.extend(qna_data.get("qna_data_list"))

                elif content_class == 'chunk':
                    for chunk_method, chunk_method_dict in context_data.get('chunk_generator').items():
                        chunking_method = chunk_method_dict.get(
                            'chunking_method')
                        for seq_no, chunk in chunk_method_dict['chunked_data'].items():
                            chunk_page_list = []
                            for key, val in chunk_method_dict['meta_data'].items():
                                if key.startswith(seq_no):
                                    pg_no = val.get("page_no")
                                    if pg_no in pages_list:
                                        chunk_page_list.append(
                                            val.get("page_no"))
                                        content_class_id = val.get(
                                            "chunk_id")
                                        CONTEXT = chunk
                                        if min_content_char_length:
                                            if len(CONTEXT) <= min_content_char_length:
                                                continue

                                        # Function Call to generate qna chunk wise
                                        qna_response_data = qna_generator_obj.generate_qna(
                                            [CONTEXT], custom_meta_data)
                                        qna_data = json.loads(json.dumps(
                                            qna_response_data, default=lambda o: o.__dict__, indent=4))
                                        for qna_dict in qna_data.get("qna_data_list"):
                                            qna_dict["content_class"] = content_class
                                            qna_dict["content_type"] = chunking_method
                                            qna_dict["content_class_id"] = content_class_id
                                            qna_dict["document_name"] = document_data.metadata.standard_data.filename.value
                                            qna_dict["page_no"] = chunk_page_list
                                            qna_dict["doc_id"] = document_data.document_id
                                            qna_dict["technique_name"] = technique_name
                                            qna_dict["llm_name"] = [llm_namespace.rsplit(
                                                '.', 1)[-1] for llm_namespace in llm_providers.values()]
                                            qna_dict["qna_strategy_name"] = qna_strategy_name.rsplit(
                                                '.', 2)[-1]
                                qna_data_list.extend(
                                    qna_data.get("qna_data_list"))

                qna_data_json = json.dumps(qna_data_list, indent=4)

                work_file_path = context_data.get(
                    'request_creator').get('work_file_path')
                work_folder_path = f"{work_file_path}_files"
                file_path = f"{work_folder_path}/qna_data.json"
                self.__file_sys_handler.write_file(file_path, qna_data_json)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "qna_file_path": file_path
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def lookp_up_page(self, total_pages, page_list):
        pages = []
        for pnum in page_list:
            pnum = pnum if (isinstance(pnum, str) and ((
                ":" in pnum) or ("-" in pnum))) else int(pnum)
            if isinstance(pnum, str):
                num_arr = [int(num)
                           for num in re.split('-|:', pnum) if len(num) > 0]
                if bool(re.match(r'^-?[0-9]+\:{1}-?[0-9]+$', pnum)):
                    page_arr = self.__get_range_val(total_pages+1)
                    if (num_arr[0] < 0 and num_arr[1] < 0) or (num_arr[0] > 0 and num_arr[1] > 0):
                        num_arr.sort()
                    num_arr[0] = num_arr[0] if num_arr[0] > 0 else num_arr[0]-1
                    num_arr[1] = num_arr[1] + \
                        1 if num_arr[1] > 0 else num_arr[1]

                    pages += page_arr[num_arr[0]: num_arr[1]]
                elif bool(re.match(r'^-?[0-9]+\:{1}$', pnum)):
                    page_arr = self.__get_range_val(total_pages)
                    pages += page_arr[num_arr[0]:]
                elif bool(re.match(r'^\:{1}-?[0-9]+$', pnum)):
                    page_arr = self.__get_range_val(
                        total_pages+1, position=1)
                    pages += page_arr[:num_arr[0]]
                else:
                    raise Exception
            elif pnum < 0:
                pages += [self.__get_range_val(
                    total_pages, position=1)[pnum]]
            elif pnum > 0:
                pages.append(pnum)
            else:
                raise Exception
        return pages

    def __get_range_val(self, n, position=0):
        return [i for i in range(position, n+1)]
