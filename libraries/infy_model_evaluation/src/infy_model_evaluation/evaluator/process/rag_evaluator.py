# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
This class is the implementation for the process layer
"""
import json
import logging
import traceback
import pandas as pd
import infy_fs_utils
from infy_model_evaluation.common.constants import Constants
from infy_model_evaluation.common.logger_factory import LoggerFactory
from infy_model_evaluation.data.config_data import EvaluatorConfigData
from infy_model_evaluation.data.dataset import EvaluatorDataset
from infy_model_evaluation.data.dataset import DatasetEntry
from infy_model_evaluation.evaluator.service.provider.open_ai_provider import OpenAIProvider
from infy_model_evaluation.evaluator.service.provider.custom_llm_provider import CustomLlmProvider
from infy_model_evaluation.evaluator.service.provider.ragas_provider import RagasProvider


class RagEvaluator():
    """Class for Rag evaluator"""

    def __init__(self) -> None:

        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        if infy_fs_utils.manager.FileSystemManager().has_fs_handler():
            self.__fs_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler()

    def evaluate(self, evaluator_config_data: EvaluatorConfigData, dataset: EvaluatorDataset):
        """   This method does the processing required and initiates the evaluation."""
        provider_result_list = []
        valid_dataset_files = []
        try:
            if not dataset:
                valid_dataset_files = self.__validate_dataset_files(
                    evaluator_config_data.datasource.file_path)
                if not valid_dataset_files:
                    raise ValueError(Constants.NO_VALID_DATASET)
                else:
                    self.__logger.info(
                        "List of valid dataset files %s", valid_dataset_files)
                    dataset = self.__prepare_dataset(valid_dataset_files)
            if evaluator_config_data.context_filter != -1:
                self.__filter_contexts(
                    evaluator_config_data.context_filter, dataset)
            if not evaluator_config_data.evaluation_only:
                target_llm_config = evaluator_config_data.target_llm
                file_path = target_llm_config.prompt_template.file_path
                if file_path:
                    target_llm_config.prompt_template = self.__fs_handler.read_file(
                        file_path)
                self.__logger.info(
                    "Fetching answers using : %s", target_llm_config.api_url)
                if target_llm_config.api_type == Constants.API_TYPE_OPENAI:
                    answer_provider = OpenAIProvider()
                    answer_provider.fetch_answers(
                        target_llm_config, dataset)
                else:
                    answer_provider = CustomLlmProvider()
                    answer_provider.fetch_answers(
                        target_llm_config, dataset)
            provider = RagasProvider()
            provider_result_list = provider.evaluate(
                evaluator_config_data, dataset)
            concatenated_df = pd.concat(provider_result_list)
            concatenated_df.reset_index(drop=True, inplace=True)
            prvider_result_json_str = concatenated_df.to_json()
            provider_result_json = json.loads(
                prvider_result_json_str)
            mean_scores_json = self.__compute_mean_scores(
                evaluator_config_data, prvider_result_json_str)
            metadata = evaluator_config_data.result.meta_data
            datasource = {'files': valid_dataset_files}
            eval_result_json = {
                'records': provider_result_json, 'aggregation': mean_scores_json, 'metadata': metadata, 'datasource': datasource}
            formatted_eval_result_json_str = json.dumps(
                eval_result_json, ensure_ascii=False, indent=4)
            file_path = evaluator_config_data.result.file_path
            if not file_path:
                file_path = '/' + Constants.DEFAULT_EVAL_RESULT_FILE_PATH
                self.__logger.info(
                    "Evaluation result file path not provided.Defaulting to %s", file_path)
            self.__fs_handler.write_file(
                file_path, formatted_eval_result_json_str, encoding='utf8')
            self.__logger.info("Result file %s created", file_path)

        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e
        return eval_result_json

    def __filter_contexts(self, context_filter, dataset):
        self.__logger.info(
            "Filtering contexts based on context_filter :%s", context_filter)
        for entry in dataset:
            entry.contexts = entry.contexts[:context_filter]

    def __compute_mean_scores(self, evaluator_config_data, json_data):
        data = pd.read_json(json_data)
        mean_scores = {}
        for metric in evaluator_config_data.metrics:
            axis = metric
            if axis in data and not data[axis].isna().all():
                axis_mean = data[axis].mean()
                mean_scores[axis] = axis_mean
                self.__logger.debug("Average score of metric %s: %s",
                                    axis, axis_mean)
            else:
                self.__logger.debug("All scores of metric %s are NaN.", axis)
        return mean_scores

    def __prepare_dataset(self, valid_dataset_files) -> EvaluatorDataset:

        dataset = []
        for file_path in valid_dataset_files:
            dataset_file_content = self.__fs_handler.read_file(file_path)
            dataset_file_content_json = json.loads(dataset_file_content)
            for entry in dataset_file_content_json:
                additional_data = {}
                dataset_entry = DatasetEntry(
                    **{
                        "question": entry.get('question'),
                        "contexts": entry.get('contexts'),
                        "ground_truth": entry.get('ground_truth'),
                        "answer": entry.get('answer'),
                    }
                )
                for key in entry.keys():
                    if key not in ('question', 'contexts', 'ground_truth', 'answer'):
                        additional_data[key] = entry.get(key)
                dataset_entry.additional_data = additional_data
                dataset.append(dataset_entry)
        return dataset

    def __validate_dataset_files(self, file_path):
        """This is a helper method to validate the dataset files"""
        fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        logger = LoggerFactory().get_logger()
        valid_dataset_files = []
        if self.__fs_handler.exists(file_path):
            json_files = fs_handler.list_files(file_path, '*.json')
            if json_files:
                for file_path in json_files:
                    dataset_file_content = fs_handler.read_file(file_path)
                    dataset_file_content_json = json.loads(
                        dataset_file_content)
                    for entry in dataset_file_content_json:
                        keys = entry.keys()
                        if 'question' not in keys or 'contexts' not in keys:
                            logger.error(
                                "%s is not a valid dataset file", file_path)
                            break
                        else:
                            valid_dataset_files.append(file_path)
                            break
            else:
                logger.error(
                    "The datasource file path %s does not contain any JSON files", file_path)
                raise FileNotFoundError(
                    "The datasource file path does not contain any JSON files")
        else:
            self.__logger.error("Invalid datasource file path %s", file_path)
            raise FileNotFoundError("Invalid datasource file path")
        return valid_dataset_files
