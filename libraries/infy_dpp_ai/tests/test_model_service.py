# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import infy_dpp_sdk
import infy_dpp_ai
import infy_fs_utils
import json
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/CONTAINER"
PROCESSOR_INPUT_CONFIG_PATH = f"/data/config/inference_online_input_config_data.json"
BACKUP_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/BACKUP"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder, backup_folder, restore_folder):
    """Initialization method"""
    # backup fun i/p - root folder ,destination_backup_folder usinf os.
    # restore fun from backuo to Storage folder
    backup_folder(f"{STORAGE_ROOT_PATH}/data/cache", BACKUP_ROOT_PATH)
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['document_data.json', f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files",
            f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files"],
        ['inference_online_input_config_data.json', f"{SAMPLE_ROOT_PATH}/data/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['extractor_attribute_prompt_2.txt', f"{SAMPLE_ROOT_PATH}/data/config/prompt_templates",
            f"{STORAGE_ROOT_PATH}/data/config/prompt_templates"],
        ['*.txt', f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"],
        ['*.json', f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"],
        ['*.pkl', f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/vectordb/encoded",
            f"{STORAGE_ROOT_PATH}/vectordb/encoded"],
        ['*.faiss', f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/vectordb/encoded",
            f"{STORAGE_ROOT_PATH}/vectordb/encoded"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)
    restore_folder(f"{BACKUP_ROOT_PATH}/cache",
                   f"{STORAGE_ROOT_PATH}/data/cache")

    # Configure file system handler
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
        infy_dpp_sdk.common.Constants.FSH_DPP)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)

    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            # "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_dpp_sdk",
                # "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
        logging_config_data, file_sys_handler)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).set_root_handler_name(infy_dpp_sdk.common.Constants.FSLH_DPP)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).add_fs_logging_handler(file_sys_logging_handler)

    # Configure client properties
    client_config_data = infy_dpp_sdk.ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        })
    infy_dpp_sdk.ClientConfigManager().load(client_config_data)
    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_model_service():
    """
        Test case for segmentation_pipeline
    """
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
    document_data_json = json.loads(file_sys_handler.read_file
                                    ("/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json"))
    # User input i.e. question and top_k are dynamically added into the input config file
    question = "What is the percentage of women employees?"
    top_k = 2
    temperature = 0.5
    query_dict = {
        "attribute_key": "generic_attribute_key",
        "question": question,
        "top_k": top_k,
        "pre_filter_fetch_k": 10,
        "filter_metadata": {}
    }
    cache_enabled = True

    input_config_data = json.loads(file_sys_handler.read_file(
        PROCESSOR_INPUT_CONFIG_PATH))
    input_config_data['processor_input_config']['QueryRetriever']['queries'] = [
        query_dict]
    for llm_name, llm_detail in input_config_data['processor_input_config']['Reader']['llm'].items():
        if llm_detail.get('enabled'):
            get_llm_config = llm_detail.get('configuration')
            get_llm_config['temperature'] = temperature
            cache = llm_detail.get('cache')
            if cache:
                cache['enabled'] = cache_enabled
    file_sys_handler.write_file(
        PROCESSOR_INPUT_CONFIG_PATH, json.dumps(input_config_data, indent=4))
    print(input_config_data)

    # --------- Run the pipeline ------------#
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])
    # --------- Save the response data to temp file ------------
    for response_data in response_data_list:
        output_file_path = "/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/processor_response_data.json"
        file_sys_handler.write_file(
            output_file_path, json.dumps(response_data.dict(), indent=4))
        assert response_data.context_data.get(
            'query_retriever').get('queries') is not None
        assert response_data.context_data.get('reader')


# api/v1/model/inference/prompt
def test_model_service_prompt():
    """
        Test case for segmentation_pipeline
    """
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
    document_data_json = json.loads(file_sys_handler.read_file
                                    ("/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json"))
    # User input i.e. question and top_k are dynamically added into the input config file
    question = "What is the percentage of women employees?"
    top_k = 2
    temperature = 0.5
    query_dict = {
        "attribute_key": "generic_attribute_key",
        "question": question,
        "top_k": top_k,
        "pre_filter_fetch_k": 10,
        "filter_metadata": {}
    }
    cache_enabled = True
    # Eg.1.
    content = ["Use the following pieces of context to answer the question at the end.",
               "If you don't know the answer or even doubtful a bit, just say that you don't know,",
               " don't try to make up an answer.Just give the shortest and most appropriate relavant answer to the question.",
               "{context}",
               "Question: {question}",
               "Helpful Answer:"
               ]
    # Eg.2.
    # content=[
    #       "Use the following pieces of context to answer the question at the end.If you don't know the answer or even doubtful a bit,just say that you don't know, don't try to make up an answer.Just give the shortest and most appropriate relavant answer to the question and the chunks IDs from which the answer is generated along with respective page_no,sequence_no.It can be single or multiple chunks.The output should be in a proper json format as below: start with key as \"answer\" and its value,then key as \"sources\" which contains its value as a list having keys as \"chunk_id\",\"page_no\",\"sequence_no\" and there respective value and last key will be how confident are you about the answer on the scale of 1 to 100 as \"confidence_pct\" here 100 means highest confidence level.This output json format should be strictly followed even when answer is not found and mandatorily contain all keys(\"answer\", \"sources\", \"chunk_id\", \"page_no\", \"sequence_no\") at all times in the output.\n\n{context}\n\nQuestion: {question}\nHelpful Answer:"
    # ]
    input_config_data = json.loads(file_sys_handler.read_file(
        PROCESSOR_INPUT_CONFIG_PATH))
    input_config_data['processor_input_config']['QueryRetriever']['queries'] = [
        query_dict]
    for llm_name, llm_detail in input_config_data['processor_input_config']['Reader']['llm'].items():
        if llm_detail.get('enabled'):
            get_llm_config = llm_detail.get('configuration')
            get_llm_config['temperature'] = temperature
            cache = llm_detail.get('cache')
            if cache:
                cache['enabled'] = cache_enabled
    prompt_template = input_config_data['processor_input_config']['Reader']["inputs"][0].get(
        "prompt_template")
    existing_content_list = input_config_data['processor_input_config']['Reader']["named_prompt_templates"].get(prompt_template)[
        'content']
    input_config_data['processor_input_config']['Reader']["named_prompt_templates"].get(
        prompt_template)['content'] = content
    file_sys_handler.write_file(
        PROCESSOR_INPUT_CONFIG_PATH, json.dumps(input_config_data, indent=4))
    print(input_config_data)

    # --------- Run the pipeline ------------#
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])
    # Restore the content in config file to original content
    input_config_data['processor_input_config']['Reader']["named_prompt_templates"].get(
        prompt_template)['content'] = existing_content_list
    file_sys_handler.write_file(
        PROCESSOR_INPUT_CONFIG_PATH, json.dumps(input_config_data, indent=4))
    # --------- Save the response data to temp file ------------
    for response_data in response_data_list:
        output_file_path = "/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/processor_response_data.json"
        file_sys_handler.write_file(
            output_file_path, json.dumps(response_data.dict(), indent=4))
        assert response_data.context_data.get(
            'query_retriever').get('queries') is not None
        assert response_data.context_data.get('reader')
