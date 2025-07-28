# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import infy_dpp_sdk
from langchain_openai import AzureOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI
from infy_model_evaluation.evaluator.process.rag_evaluator import RagEvaluator
from infy_model_evaluation.data.config_data import EvaluatorMetrics, Result, TargetLlm, Datasource
from infy_model_evaluation.data.config_data import EvaluatorConfigData
from infy_model_evaluation.data.config_data import OpenAIFormatCustomChatLlm
from infy_model_evaluation.data.config_data import OpenAIFormatCustomEmbedding
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData


PROCESSEOR_CONTEXT_DATA_NAME = "rag_evaluator"


class RagEvaluation(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = ProcessorResponseData()
        rag_evaluator_config_data = config_data.get('RagEvaluation', {})
        # org_files_full_path = context_data['request_creator']['work_file_path']
        # from_files_full_path = __get_temp_file_path(org_files_full_path)

        request_config_data = rag_evaluator_config_data.get(
            'model_evaluation_config', {})

        evaluator_config_data = request_config_data.get('evaluator', {})
        target_config_data = request_config_data.get('target', {})
        datasource_config_data = request_config_data.get('datasource', {})
        result_config_data = request_config_data.get('result', {})
        datasource_config = datasource_config_data.get('configuration')
        result_config = result_config_data.get('configuration')

        llm_config = {}
        llm_config_custom = {}
        embedding_config = {}
        embedding_config_custom = {}
        metrics = {}
        evaluation_only = True
        context_filter = -1

        # Prepare Evaluator Config
        for key, value in evaluator_config_data.items():
            if key == 'embedding':
                embedding_config = self.__get_openai_config(value)
                embedding_config_custom = self.__get_custom_config(value)
                continue
            if key == 'llm':
                llm_config = self.__get_openai_config(value)
                llm_config_custom = self.__get_custom_config(value)
                continue
            if key == 'metrics_list':
                metrics = []
                for metric in value:
                    if metric.get('enabled'):
                        metrics.append(metric.get('name'))
                continue
            if key == 'evaluation_only':
                evaluation_only = value
                continue
            if key == 'context_filter':
                context_filter = value

        for key, value in target_config_data.items():
            if key == 'llm':
                target_llm_config = value.get('configuration')
                break

        evaluator_embedding = None
        evaluator_custom_embedding = None
        # Prepare evaluator embedding config
        tiktoken_cache_dir = None
        if embedding_config:
            tiktoken_cache_dir = embedding_config.get(
                'tiktoken_cache_dir')
            evaluator_embedding = AzureOpenAIEmbeddings(
                **{
                    "openai_api_type": embedding_config.get('api_type'),
                    "azure_endpoint": embedding_config.get('api_url'),
                    "api_key": embedding_config.get('api_key'),
                    "openai_api_version": embedding_config.get('api_version'),
                    "model": embedding_config.get('model_name'),
                    "azure_deployment": embedding_config.get('deployment_name'),
                }
            )
        elif embedding_config_custom:
            tiktoken_cache_dir = embedding_config_custom.get(
                'tiktoken_cache_dir')
            evaluator_custom_embedding = OpenAIFormatCustomEmbedding(
                **embedding_config_custom)

        # Prepare evaluator llm config
        evaluator_llm_chat = None
        evaluator_llm = None
        evaluator_custom_llm_chat = None
        is_chat_model = False
        if llm_config:
            is_chat_model = llm_config.get('is_chat_model')
            if is_chat_model:
                evaluator_llm_chat = AzureChatOpenAI(
                    **{
                        "openai_api_type": llm_config.get('api_type'),
                        "azure_endpoint": llm_config.get('api_url'),
                        "api_key": llm_config.get('api_key'),
                        "openai_api_version": llm_config.get('api_version'),
                        "model": llm_config.get('model_name'),
                        "azure_deployment": llm_config.get('deployment_name'),
                    }
                )
            else:
                evaluator_llm = AzureOpenAI(
                    **{
                        "openai_api_type": llm_config.get('api_type'),
                        "azure_endpoint": llm_config.get('api_url'),
                        "api_key": llm_config.get('api_key'),
                        "openai_api_version": llm_config.get('api_version'),
                        "model": llm_config.get('model_name'),
                        "azure_deployment": llm_config.get('deployment_name'),
                    }
                )
        elif llm_config_custom:
            is_chat_model = llm_config_custom.get('is_chat_model')
            if is_chat_model:
                evaluator_custom_llm_chat = OpenAIFormatCustomChatLlm(
                    **llm_config_custom)

        # Prepare evaluator metics config
        evaluator_metrics = EvaluatorMetrics(
            **{
                "metrics": metrics
            }
        )

        # Prepare target llm config
        __target_llm = TargetLlm(**target_llm_config)

        # if not result_config.get('file_path'):
        #     result_config['file_path'] = context_data['request_creator']['work_file_path'] + \
        #         "_files/rag_metrics.json"
        metric_folder_path = context_data['request_creator']['metric_folder_path']
        self.__logger.debug("metric_folder_path::%s", metric_folder_path)
        if not result_config.get('file_path'):
            result_config['file_path'] = metric_folder_path + \
                "/rag_metrics.json"

        __result = Result(**result_config)

        result_folder_path = context_data['request_creator']['result_folder_path']
        self.__logger.debug("result_folder_path::%s", result_folder_path)
        if not datasource_config.get('file_path'):
            datasource_config['file_path'] = result_folder_path

        __datasource = Datasource(**datasource_config)

        # Prepare evaluator config data
        evaluator_config_data = EvaluatorConfigData(
            embedding=evaluator_embedding,
            custom_embedding=evaluator_custom_embedding,
            llm=evaluator_llm,
            llm_chat=evaluator_llm_chat,
            custom_llm_chat=evaluator_custom_llm_chat,
            metrics=evaluator_metrics.metrics,
            target_llm=__target_llm,
            evaluation_only=evaluation_only,
            context_filter=context_filter,
            result=__result,
            datasource=__datasource,
            is_evaluator_llm_chat_model=is_chat_model,
            evaluator_embedding_tiktoken_cache_dir=tiktoken_cache_dir
        )

        evaluator = RagEvaluator()
        try:
            result = evaluator.evaluate(evaluator_config_data, [])
        except Exception as e:
            self.__logger.error("Error in evaluating RAG model: %s", str(e))
            raise e

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "rag_metrics_file": result_config.get('file_path')
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __get_openai_config(self, value):
        """This is a helper method to retrieve openai config for embeddings and llm"""
        config = {}
        for key, val in value.items():
            if key == "openai":
                if val.get('enabled'):
                    config = val.get('configuration')
                    break
        return config

    def __get_custom_config(self, value):
        """This is a helper method to retrieve custom config for embeddings and llm"""
        config = {}
        for key, val in value.items():
            if key == "custom":
                if val.get('enabled'):
                    config = val.get('configuration')
                    break
        return config
