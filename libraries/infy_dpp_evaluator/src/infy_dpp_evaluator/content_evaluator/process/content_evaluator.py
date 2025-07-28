# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import json
import importlib
import infy_dpp_sdk
import infy_gen_ai_sdk
import pandas as pd
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
import infy_model_evaluation
from ...common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "content_evaluator"


class ContentEvaluator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__app_config = self.get_app_config()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        try:
            processor_response_data = ProcessorResponseData()
            content_evaluator_config_data = config_data.get(
                'ContentEvaluator', {})
            org_files_full_path = context_data['request_creator']['work_file_path']
            from_files_full_path = __get_temp_file_path(org_files_full_path)
            output_metric_folder_path = context_data['request_creator']['metric_folder_path']
            truth_data_file_path = from_files_full_path
            qna_metrics_list = []
            metric_provider_obj_list = []

            for technique in content_evaluator_config_data.get('techniques', []):
                if not technique.get("enabled"):
                    continue
                else:
                    metrics_name_in_tech = technique.get(
                        "metrics_name")
                    llm_name = technique.get("llm_name")
                    metrics_llm_type = llm_name.split('.')[1]

                    for llm_type, llm_value in content_evaluator_config_data.get('llm').items():
                        if metrics_llm_type == llm_type:
                            if llm_type == 'openai':
                                if llm_value.get('enabled'):
                                    get_llm = llm_type
                                    get_llm_config = llm_value.get(
                                        'configuration')
                                    break
                            elif llm_type == 'openai_lite':
                                if llm_value.get('enabled'):
                                    get_llm = llm_type
                                    get_llm_config = llm_value.get(
                                        'configuration')
                                    break
                            elif llm_type == 'custom':
                                for custom_llm_key, custom_llm_val in llm_value.items():
                                    if custom_llm_val.get('enabled'):
                                        get_llm = llm_type
                                        get_llm_config = custom_llm_val.get(
                                            'configuration')
                                        json_payload_dict = custom_llm_val.get(
                                            'json_payload')
                                        headers = custom_llm_val.get(
                                            'headers', None)
                                        custom_llm_name = custom_llm_key
                                        break

                    if metrics_llm_type == get_llm and get_llm == "openai_lite":
                        llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
                            infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
                                **get_llm_config))
                    elif metrics_llm_type == get_llm and get_llm == "openai":
                        llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
                            infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
                            )
                        )
                    elif metrics_llm_type == get_llm and get_llm == "custom":
                        if headers:
                            llm_provider = infy_model_evaluation.llm.provider.ChatLlmProvider(
                                infy_model_evaluation.llm.provider.ChatLlmProviderConfigData(
                                    **{
                                        "api_url": get_llm_config.get("inference_url"),
                                        "json_payload": json_payload_dict,
                                        "headers":  headers,
                                        "model_name": custom_llm_name
                                    }
                                ))
                        else:
                            llm_provider = infy_model_evaluation.llm.provider.CustomLlmProvider(
                                infy_model_evaluation.llm.provider.CustomLlmProviderConfigData(
                                    **{"api_url": get_llm_config.get(
                                        'inference_url'),
                                        "model_name": custom_llm_name,
                                        "json_payload": json_payload_dict
                                       }
                                )
                            )

                    for metrics_name, metrics_dict in content_evaluator_config_data.get('metrics').items():
                        if metrics_name == metrics_name_in_tech:
                            if metrics_dict.get('enabled'):
                                metrics_properties = metrics_dict.get(
                                    'properties')
                                llm_res_parser_name = metrics_properties.get(
                                    "llm_res_parser")
                                prompt_template_file_dict = metrics_properties.get(
                                    "prompt_template_file_dict")
                                break

                    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
                        "llm_provider_obj": llm_provider,
                        "llm_res_parser_obj": self.__get_llm_res_parser_obj(llm_res_parser_name) if llm_res_parser_name else None
                    })
                    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
                        __root__={"openai_llm_provider": llm_provider_data})]

                    if metrics_name_in_tech == "racar":
                        metric_provider_obj = infy_model_evaluation.content_evaluator.RACARProvider(
                            llm_config_data_list)
                        # Optional: Read prompt template file and set it in the metric_provider_obj
                        self.__set_user_defined_prompt_template_dict(
                            metric_provider_obj, prompt_template_file_dict)
                        metric_provider_obj_list.append(
                            metric_provider_obj)
                    elif metrics_name_in_tech == "qa_eval":
                        metric_provider_obj = infy_model_evaluation.content_evaluator.QAEvalProvider(
                            llm_config_data_list)
                        self.__set_user_defined_prompt_template_dict(
                            metric_provider_obj, prompt_template_file_dict)
                        metric_provider_obj_list.append(
                            metric_provider_obj)

            # After looping through all techinques, pass metric_provider_obj_list to QnaEvaluator object and evaluate
            qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
                metric_provider_obj_list)

            # Read the Excel file
            df = pd.read_excel(truth_data_file_path)
            # Loops through each row and pass required columns to the evaluate function
            for index, row in df.iterrows():
                q_no = row['Q_No']
                question = row['Question']
                answer = row['Ground_Truth']
                contexts = row['Answer_Source']

                content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
                    **{
                        "question": question,
                        "contexts": contexts,
                        "answer": answer
                    }
                )
                response_metrics_data = qna_evaluator_obj.evaluate(
                    content_evaluator_req_data)
                response_metrics_data_dict = response_metrics_data.dict().get("metrics")
                response_metrics_data_dict['Q_No'] = q_no
                qna_metrics_list.append(response_metrics_data_dict)
            # Save response_metrics_data into a json file
            output_qna_metrics_file_path = f"{output_metric_folder_path}/qna_metrics.json"
            self.__file_sys_handler.write_file(
                output_qna_metrics_file_path, json.dumps(qna_metrics_list, indent=4))
        except Exception as e:
            print("ERROR: ", e)
            self.__logger.error(e)
            # Save response_metrics_data into a json file
            output_qna_metrics_file_path = f"{output_metric_folder_path}/qna_metrics.json"
            self.__file_sys_handler.write_file(
                output_qna_metrics_file_path, json.dumps(qna_metrics_list, indent=4))

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "qna_metrics_file_path": output_qna_metrics_file_path
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __get_llm_res_parser_obj(self, llm_res_parser_name):
        namespace, res_parser_class_name = llm_res_parser_name.rsplit(
            ".", 1)
        library = importlib.import_module(
            namespace)
        llm_res_parser_obj: infy_model_evaluation.llm.interface.ILLMResponseParserProvider = getattr(
            library, res_parser_class_name)()
        return llm_res_parser_obj

    def __set_user_defined_prompt_template_dict(self, metric_provider_obj, prompt_template_file_dict):
        prompt_template_dict = metric_provider_obj.get_prompt_template_dict()
        for prompt_template_file_name, prompt_template_file_path in prompt_template_file_dict.items():
            if prompt_template_file_path:
                prompt_template_dict[prompt_template_file_name] = self.__file_sys_handler.read_file(
                    prompt_template_file_path)
                metric_provider_obj.set_prompt_template_dict(
                    prompt_template_dict)
