# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""
import os
import time
import json
from typing import List
import pytest
from langchain_openai import AzureOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI

import infy_fs_utils
import infy_model_evaluation
from infy_model_evaluation.common.constants import Constants
from infy_model_evaluation.common.logger_factory import LoggerFactory
from infy_model_evaluation.configuration import ClientConfigData
from infy_model_evaluation.evaluator.process.rag_evaluator import RagEvaluator
from infy_model_evaluation.data.config_data import EvaluatorMetrics, Result, TargetLlm, Datasource
from infy_model_evaluation.data.config_data import EvaluatorConfigData
from infy_model_evaluation.data.dataset import EvaluatorDataset
from infy_model_evaluation.data.dataset import DatasetEntry
from infy_model_evaluation.data.config_data import OpenAIFormatCustomChatLlm
from infy_model_evaluation.data.config_data import OpenAIFormatCustomEmbedding


CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_model_evaluation/{__name__}/CONTAINER"
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_model_evaluation/{__name__}/STORAGE"


class TestEvaluator:
    """Test class"""

    def __init__(self):
        logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(Constants.FSH_MODEL_EVALUATION).get_logger()
        logger.debug("TestEvaluator")


@pytest.fixture(scope='module', autouse=True)
def setup(create_root_folders, copy_files_to_root_folder) -> dict:
    """Initialization method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"

    FILES_TO_COPY = [
        ['input_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['dataset_file.json', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['*.json', f"{SAMPLE_ROOT_PATH}/input/invalid",
            f"{STORAGE_ROOT_PATH}/data/input/invalid"],
        ['*.json', f"{SAMPLE_ROOT_PATH}/input/without_ans",
            f"{STORAGE_ROOT_PATH}/data/input/without_ans"],
        ['*.json', f"{SAMPLE_ROOT_PATH}/input/without_gt",
            f"{STORAGE_ROOT_PATH}/data/input/without_gt"],
        ['*.txt', f"{SAMPLE_ROOT_PATH}/config/prompt_templates",
            f"{STORAGE_ROOT_PATH}/data/config/prompt_templates"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)

    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })
    file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
        storage_config_data)
    infy_fs_utils.manager.FileSystemManager().set_root_handler_name(
        Constants.FSH_MODEL_EVALUATION)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)

    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            # "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_model_evaluation",
                # "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
        logging_config_data, file_sys_handler)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).set_root_handler_name(Constants.FSLH_MODEL_EVALUATION)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).add_fs_logging_handler(file_sys_logging_handler)

    # Configure client properties
    client_config_data = ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        }
    )
    infy_model_evaluation.ClientConfigManager().load(client_config_data)
    input_data = __setup_config_data()
    return input_data

    # yield  # Run all test methods
    # # Post run cleanup
    # # Delete file system handler so that other test modules don't get duplicate key error
    # infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    # infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_only_eval(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = True
    evaluator = RagEvaluator()
    dataset = __prepare_dataset(
        setup['evaluator_config_data'].datasource.file_path)
    result = evaluator.evaluate(
        setup['evaluator_config_data'], [])
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def test_only_eval_without_gt(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = True
    setup['evaluator_config_data'].result.file_path = "/evaluation_result_without_gt.json"
    evaluator = RagEvaluator()
    dataset = __prepare_dataset("data/input/without_gt")
    result = evaluator.evaluate(
        setup['evaluator_config_data'], dataset)
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_relevancy' in aggregation or 'context_utilization' in aggregation or 'context_relevancy' in aggregation


def test_only_eval_without_ans(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = True
    evaluator = RagEvaluator()
    dataset = __prepare_dataset("data/input/without_ans")
    result = evaluator.evaluate(setup['evaluator_config_data'],
                                dataset)
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def test_eval_with_fetch_ans(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = False
    setup['evaluator_config_data'].target_llm.api_type = "azure"
    # Please configure the api_url before running the test case
    setup['evaluator_config_data'].target_llm.api_url = os.environ['AZURE_OPENAI_SERVER_BASE_URL']
    setup['evaluator_config_data'].target_llm.max_tokens = 1000
    setup['evaluator_config_data'].target_llm.temperature = 0.7
    setup['evaluator_config_data'].target_llm.remove_prompt_from_response = False
    setup['evaluator_config_data'].target_llm.requires_num_return_sequences = False
    setup['evaluator_config_data'].target_llm.num_return_sequences = 1
    setup['evaluator_config_data'].target_llm.do_sample = True
    setup['evaluator_config_data'].result.file_path = "/evaluation_result_with_fetch_ans.json"
    # setup['evaluator_config_data'].target_llm.is_chat_model = True
    # setup['evaluator_config_data'].target_llm.top_p = 0.95
    # setup['evaluator_config_data'].target_llm.frequency_penalty = 0
    # setup['evaluator_config_data'].target_llm.presence_penalty = 0
    evaluator = RagEvaluator()
    dataset = __prepare_dataset(
        setup['evaluator_config_data'].datasource.file_path)
    result = evaluator.evaluate(setup['evaluator_config_data'],
                                [])
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def test_eval_with_fetch_ans_custom(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = False
    setup['evaluator_config_data'].target_llm.api_type = ""
    # Please configure the api_url before running the test case
    setup['evaluator_config_data'].target_llm.api_url = os.environ['CUSTOM_LLM_MIXTRAL_INFERENCE_URL']
    setup['evaluator_config_data'].target_llm.max_tokens = 1024
    setup['evaluator_config_data'].target_llm.temperature = 0.7
    setup['evaluator_config_data'].target_llm.remove_prompt_from_response = False
    setup['evaluator_config_data'].target_llm.requires_num_return_sequences = False
    setup['evaluator_config_data'].target_llm.num_return_sequences = 1
    setup['evaluator_config_data'].target_llm.do_sample = True
    setup['evaluator_config_data'].result.file_path = "/evaluation_result_mixtral8x7b-instruct.json"

    evaluator = RagEvaluator()
    dataset = __prepare_dataset(
        setup['evaluator_config_data'].datasource.file_path)
    result = evaluator.evaluate(setup['evaluator_config_data'],
                                [])
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def test_invalid_dataset(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = False
    evaluator = RagEvaluator()
    # dataset = []
    # dataset = __prepare_dataset("data/input/invalid")
    setup['evaluator_config_data'].datasource.file_path = "data/input/invalid"
    with pytest.raises(ValueError, match=Constants.NO_VALID_DATASET):
        result = evaluator.evaluate(setup['evaluator_config_data'], [])


def test_only_eval_custom_llm_embedding(setup):
    """This is a Test method for openAI format custom Embedding provider"""
    # Enable Evaluator Custom LLM and Evaluator Embedding config and disable openAI config in config file to run this test case
    setup['evaluator_config_data'].evaluation_only = True
    evaluator = RagEvaluator()
    dataset = __prepare_dataset(
        setup['evaluator_config_data'].datasource.file_path)
    result = evaluator.evaluate(
        setup['evaluator_config_data'], dataset)
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def test_only_eval_with_perf_metrics(setup):
    """This is a Test method"""
    setup['evaluator_config_data'].evaluation_only = True
    evaluator = RagEvaluator()
    dataset = __prepare_dataset(
        setup['evaluator_config_data'].datasource.file_path)
    start_time = time.time()
    result = evaluator.evaluate(
        setup['evaluator_config_data'], dataset)
    elapsed_time = round((time.time() - start_time), 2)
    __calculate_performance_metrics(len(dataset), len(
        setup['evaluator_config_data'].metrics), elapsed_time, 2)
    aggregation = result.get('aggregation')
    assert 'faithfulness' in aggregation or 'answer_correctness' in aggregation or 'answer_similarity' in aggregation or 'answer_relevancy' in aggregation or 'context_precision' in aggregation or 'context_utilization' in aggregation or 'context_recall' in aggregation or 'context_relevancy' in aggregation or 'context_entity_recall' in aggregation


def __setup_config_data() -> dict:
    """This method prepares the config data"""
    fs_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(Constants.FSH_MODEL_EVALUATION)

    logger = LoggerFactory().get_logger()

    file_path = "data/config/input_config.json"

    if fs_handler.exists(file_path):
        config_file_content = fs_handler.read_file(file_path)
        request_config_data = json.loads(config_file_content)
    else:
        message = f"Input config file {file_path} not found"
        logger.error(message)
        raise FileNotFoundError(message)

    evaluator_config_data = request_config_data.get('evaluator', {})
    target_config_data = request_config_data.get('target', {})
    datasource_config_data = request_config_data.get('datasource', {})
    result_config_data = request_config_data.get('result', {})
    llm_config = {}
    llm_config_custom = {}
    embedding_config = {}
    embedding_config_custom = {}
    metrics = {}
    evaluation_only = True
    context_filter = -1
    for key, value in evaluator_config_data.items():
        if key == 'embedding':
            embedding_config = __get_openai_config(value)
            embedding_config_custom = __get_custom_config(value)
            continue
        if key == 'llm':
            llm_config = __get_openai_config(value)
            llm_config_custom = __get_custom_config(value)
            continue
        if key == 'metrics_list':
            metrics = __get_enabled_metrics(value)
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
    datasource_config = datasource_config_data.get('configuration')
    result_config = result_config_data.get('configuration')

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
                "azure_endpoint": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
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
                    "azure_endpoint": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                    "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                    "openai_api_version": llm_config.get('api_version'),
                    "model": llm_config.get('model_name'),
                    "azure_deployment": llm_config.get('deployment_name'),
                }
            )
        else:
            evaluator_llm = AzureOpenAI(
                **{
                    "openai_api_type": llm_config.get('api_type'),
                    "azure_endpoint": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                    "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
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

    # Prepare evaluator metrics
    evaluator_metrics = EvaluatorMetrics(metrics=metrics)
    # Prepare target llm config
    __target_llm = TargetLlm(**target_llm_config)
    __target_llm.api_key = os.environ['AZURE_OPENAI_SECRET_KEY']
    __target_llm.api_url = os.environ['AZURE_OPENAI_SERVER_BASE_URL']

    __result = Result(**result_config)

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
    input_data = {}
    input_data['evaluator_config_data'] = evaluator_config_data
    return input_data


def __prepare_dataset(file_path) -> EvaluatorDataset:
    fs_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(Constants.FSH_MODEL_EVALUATION)
    logger = LoggerFactory().get_logger()
    if fs_handler.exists(file_path):
        valid_dataset_files = __validate_dataset_files(file_path)
        logger.info("List of valid dataset files %s", valid_dataset_files)
    else:
        logger.error("Invalid datasource file path %s::", file_path)
        raise FileNotFoundError("Invalid datasource file path")
    dataset = []
    for file_path in valid_dataset_files:
        dataset_file_content = fs_handler.read_file(file_path)
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


def __validate_dataset_files(file_path):
    """This is a helper method to validate the dataset files"""
    fs_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(Constants.FSH_MODEL_EVALUATION)
    logger = LoggerFactory().get_logger()
    valid_dataset_files = []
    json_files = fs_handler.list_files(file_path, '*.json')
    if json_files:
        for file_path in json_files:
            dataset_file_content = fs_handler.read_file(file_path)
            dataset_file_content_json = json.loads(dataset_file_content)
            for entry in dataset_file_content_json:
                keys = entry.keys()
                if 'question' not in keys or 'contexts' not in keys:
                    message = "%s is not a valid dataset file"
                    logger.error(message, file_path)
                    break
                else:
                    valid_dataset_files.append(file_path)
                    break
    else:
        message = "The directory does not contain any JSON files"
        logger.error(message)
        raise FileNotFoundError(message)
    return valid_dataset_files


def __get_openai_config(value):
    """This is a helper method to retrieve openai config for embeddings and llm"""
    config = {}
    for key, val in value.items():
        if key == "openai":
            if val.get('enabled'):
                config = val.get('configuration')
                break
    return config


def __get_enabled_metrics(metrics_list) -> List:
    """This is a helper method to prepare the evaluation metrics list"""
    metrics = []
    for metric in metrics_list:
        if metric.get('enabled'):
            metrics.append(metric.get('name'))
    return metrics


def __get_custom_config(value):
    """This is a helper method to retrieve custom config for embeddings and llm"""
    config = {}
    for key, val in value.items():
        if key == "custom":
            if val.get('enabled'):
                config = val.get('configuration')
                break
    return config


def __calculate_performance_metrics(record_count, metric_count, exec_time, ndigits):
    """This is a helper method to calculate performance metrics"""
    logger = infy_fs_utils.manager.FileSystemLoggingManager(
    ).get_fs_logging_handler(Constants.FSH_MODEL_EVALUATION).get_logger()
    logger.info("Number of records:: %s", record_count)
    logger.info("Number of metrics enabled:: %s", metric_count)
    logger.info("Total Execution time: %s secs", exec_time)
    exec_time_per_record = round((exec_time / record_count), ndigits)
    logger.info("Execution time per record: %s secs",
                exec_time_per_record)
    exec_time_per_record_per_metric = round(
        (exec_time_per_record / metric_count), ndigits)
    logger.info("Execution time per record per metric: %s secs",
                exec_time_per_record_per_metric)
