# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


"""Module for Ragas provider"""

import os
from typing import List
import logging
import time
import traceback
from ragas.evaluation import Result
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_correctness,
    answer_similarity,
    context_precision,
    context_recall,
    context_relevancy,
    context_utilization,
    context_entity_recall
)
from datasets import Dataset
import infy_fs_utils
from infy_model_evaluation.data.config_data import EvaluatorConfigData
from infy_model_evaluation.data.dataset import EvaluatorDataset
from infy_model_evaluation.evaluator.service.provider.open_ai_format_custom_llm_provider import OpenAIFormatCustomLlmProvider
from infy_model_evaluation.evaluator.service.provider.open_ai_format_custom_embedding_provider import OpenAIFormatCustomEmbeddingProvider


class RagasProvider():
    """Domain class"""

    def __init__(self) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

    def evaluate(self, eval_config: EvaluatorConfigData, dataset: EvaluatorDataset) -> List[Result]:
        """   Evaluates the model."""
        try:
            os.environ["TIKTOKEN_CACHE_DIR"] = eval_config.evaluator_embedding_tiktoken_cache_dir
            self.__logger.debug("TIKTOKEN_CACHE_DIR::%s",
                                os.getenv('TIKTOKEN_CACHE_DIR'))
            dataset_as_dict_list = self.__convert_dataset_to_dict_list(dataset)
            result_list = []
            total_records = len(dataset_as_dict_list)
            gt_dependent_metrics = self.__setup_gt_dependent_metrics()
            gt_dependent_metrics_names = map(
                lambda metric: metric.name, gt_dependent_metrics)
            self.__logger.info(
                "Metrics dependent on ground truth :%s", list(gt_dependent_metrics_names))
            ragas_metrics = self.__get_ragas_metrics(eval_config.metrics)
            if context_relevancy in ragas_metrics:
                self.__logger.warning(
                    "The 'context_relevancy' metric is going to be deprecated soon! Please use the 'context_precision' metric instead."
                )
            gt_independent_metrics = [
                item for item in ragas_metrics if item not in gt_dependent_metrics]
            evaluated_records = 0
            eval_llm = None
            if eval_config.is_evaluator_llm_chat_model:
                if eval_config.llm_chat:
                    eval_llm = eval_config.llm_chat
                elif eval_config.custom_llm_chat:
                    self.__logger.info("Using custom llm config to call ragas")
                    custom_llm = eval_config.custom_llm_chat
                    eval_llm = OpenAIFormatCustomLlmProvider(
                        **{
                            "api_url": custom_llm.api_url,
                            "api_key": custom_llm.api_key,
                            "model_name": custom_llm.model_name,
                            "deployment_name": custom_llm.deployment_name,
                            "max_tokens": custom_llm.max_tokens,
                            'temperature': custom_llm.temperature,
                            "top_p": custom_llm.top_p,
                            "frequency_penalty": custom_llm.frequency_penalty,
                            "presence_penalty": custom_llm.presence_penalty,
                            "stop": custom_llm.stop
                        })
            else:
                eval_llm = eval_config.llm
            if eval_config.embedding:
                eval_embedding = eval_config.embedding
            elif eval_config.custom_embedding:
                self.__logger.info(
                    "Using custom embedding config to call ragas")
                custom_embedding = eval_config.custom_embedding
                eval_embedding = OpenAIFormatCustomEmbeddingProvider(
                    **{
                        "api_url": custom_embedding.api_url,
                        "api_key": custom_embedding.api_key,
                        "model_name": custom_embedding.model_name,
                        "api_version": custom_embedding.api_version
                    })
            for counter, dataset_entry in enumerate(dataset_as_dict_list, start=1):
                if 'ground_truth' not in dataset_entry.features:
                    self.__logger.info(
                        "ground truth is not present in the dataset entry %s ,excluding metrics dependent on ground truth", counter)
                    result = evaluate(dataset_entry, metrics=gt_independent_metrics,
                                      llm=eval_llm, embeddings=eval_embedding, raise_exceptions=True)
                else:
                    result = evaluate(dataset_entry, metrics=ragas_metrics,
                                      llm=eval_llm, embeddings=eval_embedding, raise_exceptions=True)
                result_pd = result.to_pandas()
                result_list.append(result_pd)
                evaluated_records = counter
                self.__logger.debug(
                    "Evaluated %s out of %s records.", evaluated_records, total_records)
                if evaluated_records < total_records:
                    time.sleep(5)
            self.__logger.info(
                "Evaluation completed for %s dataset records!", evaluated_records)
        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e
        return result_list

    def __setup_gt_dependent_metrics(self):
        gt_dependent_metrics = []
        gt_dependent_metrics.append(answer_correctness)
        gt_dependent_metrics.append(answer_similarity)
        gt_dependent_metrics.append(context_recall)
        gt_dependent_metrics.append(context_precision)
        gt_dependent_metrics.append(context_entity_recall)
        return gt_dependent_metrics

    def __get_ragas_metrics(self, metrics):
        ragas_metrics = []
        for metric in metrics:
            if metric == 'faithfulness':
                ragas_metrics.append(faithfulness)
                continue
            if metric == 'answer_relevancy':
                ragas_metrics.append(answer_relevancy)
                continue
            if metric == 'context_recall':
                ragas_metrics.append(context_recall)
                continue
            if metric == 'context_precision':
                ragas_metrics.append(context_precision)
                continue
            if metric == 'answer_correctness':
                ragas_metrics.append(answer_correctness)
                continue
            if metric == 'answer_similarity':
                ragas_metrics.append(answer_similarity)
                continue
            if metric == 'context_utilization':
                ragas_metrics.append(context_utilization)
                continue
            if metric == 'context_relevancy':
                ragas_metrics.append(context_relevancy)
                continue
            if metric == 'context_entity_recall':
                ragas_metrics.append(context_entity_recall)
                continue
        return ragas_metrics

    def __convert_dataset_to_dict_list(self, dataset):
        """converts the dataset to dict list"""
        dataset_as_dict_list = []
        for dataset_entry in dataset:
            dataset_entry_as_dict = dataset_entry.dict()
            if 'ground_truth' in dataset_entry_as_dict and (dataset_entry_as_dict.get('ground_truth') == '' or dataset_entry_as_dict.get('ground_truth') is None):
                dataset_entry_as_dict.pop('ground_truth')
            self.__handle_additional_data(dataset_entry_as_dict)
            self.__format_values(dataset_entry_as_dict)
            dataset_as_dict_list.append(
                Dataset.from_dict(dataset_entry_as_dict))
        self.__logger.debug(
            'Converted dataset to a list of dict')

        return dataset_as_dict_list

    def __handle_additional_data(self, dataset_entry_as_dict):
        """handles the additional data in the dataset entry"""
        additional_data = dataset_entry_as_dict.get('additional_data')
        counter = 0
        keys = list(additional_data.keys())
        for key in keys:
            dataset_entry_as_dict[key] = additional_data.pop(key)
            counter += 1
        dataset_entry_as_dict.pop('additional_data')

    def __format_values(self, dataset_entry_as_dict) -> None:
        """formats the values in the dataset entry"""
        for name, value in dataset_entry_as_dict.items():
            value = [value]
            dataset_entry_as_dict[name] = value
