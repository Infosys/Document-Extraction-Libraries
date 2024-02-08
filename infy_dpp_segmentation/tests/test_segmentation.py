# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import os
import infy_dpp_sdk
import infy_dpp_segmentation as infy_dpp_segmt_lib


# DATA_FOLDER_PATH = os.path.abspath('./data/test/infy_annual')
DATA_FOLDER_PATH = os.path.abspath('./data/test/swp')
PROCESSOR_INPUT_CONFIG_PATH = os.path.abspath(
    './data/test/config/sample2_pipeline_input_config_data.json')
TEST_OUTPUT_FOLDER_PATH = os.path.abspath('./data/test/output')


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    os.chdir('src')
    # Configure client properties
    CLIENT_CONFIG_DATA_DICT = {
        "storage_data": {
            "storage_uri": f"file:///{DATA_FOLDER_PATH}",
            "storage_server_url": None,
            "storage_access_key": None,
            "storage_secret_key": None
        },
        "container_data": {
            "container_root_path": f"{DATA_FOLDER_PATH}",
        }
    }
    infy_dpp_segmt_lib.ConfigurationManager().load(
        infy_dpp_segmt_lib.ClientConfigData(**CLIENT_CONFIG_DATA_DICT))


def test_segmentation_pipeline_1():
    """
    Test case for segmentation_pipeline
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_segmentation_pipeline.json"

    # Segment Generator
    segment_generator = infy_dpp_segmt_lib.segment_generator.SegmentGenerator()
    response_data = segment_generator.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('segment_generator') is not None

    # Segment Parser
    segment_parser = infy_dpp_segmt_lib.segment_parser.SegmentDataParser()
    response_data = segment_parser.do_execute(response_data.document_data, response_data.context_data,
                                              config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('segment_data_parser') is not None

    # Chunk Parser
    chunk_parser = infy_dpp_segmt_lib.chunk_generator.ChunkDataParser()
    response_data = chunk_parser.do_execute(response_data.document_data, response_data.context_data,
                                            config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('chunk_data_parser') is not None

    # Chunk Saver
    chunk_saver = infy_dpp_segmt_lib.chunk_saver.SaveChunkDataParser()
    response_data = chunk_saver.do_execute(response_data.document_data, response_data.context_data,
                                           config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('save_chunk_data') is not None


def test_segmentation_pipeline_2():
    """
        Test case for segmentation_pipeline
    """
    # -------- Document Data -----------
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")

    # -------- Config Data -----------
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)

    # --------- Run the pipeline ------------
    orchestrator_native_obj: infy_dpp_sdk.interface.i_orchestrator_native.IOrchestratorNative = None
    orchestrator_native_obj = infy_dpp_sdk.orchestrator.controller.OrchestratorNativeBasic(
        config_data_json)
    response_data_list = orchestrator_native_obj.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])

    # --------- Save the response data to temp file ------------
    for idx, response_data in enumerate(response_data_list):
        output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_segmentation_pipeline_2_{idx}.json"
        infy_dpp_segmt_lib.common.FileUtil.save_to_json(
            output_file_path, response_data.dict())
        assert response_data.context_data.get('save_chunk_data') is not None


def test_segment_generator_1():
    """
    Test case for segmentation
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_segment_generator.json"

    segment_generator = infy_dpp_segmt_lib.segment_generator.SegmentGenerator()
    response_data = segment_generator.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('segment_generator') is not None


def test_segment_generator_2():
    """
    Test case for segmentation
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/sample2_document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/sample2_document_data_segment_generator.json"

    segment_generator = infy_dpp_segmt_lib.segment_generator.SegmentGenerator()
    response_data = segment_generator.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('segment_generator') is not None


def test_segment_parser_1():
    """
    Test case for segment parser
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_segment_parser.json"

    segment_parser = infy_dpp_segmt_lib.segment_parser.SegmentDataParser()
    response_data = segment_parser.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('segment_data_parser') is not None


def test_chunk_parser_1():
    """
    Test case for chunk parser
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_chunk_parser.json"

    chunk_parser = infy_dpp_segmt_lib.chunk_generator.ChunkDataParser()
    response_data = chunk_parser.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('chunk_data_parser') is not None


def test_chunk_saver_1():
    """
    Test case for chunk saver
    """
    document_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        f"{DATA_FOLDER_PATH}/document_data.json")
    config_data_json = infy_dpp_segmt_lib.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH)
    output_file_path = f"{TEST_OUTPUT_FOLDER_PATH}/document_data_chunk_saver.json"
    chunk_saver = infy_dpp_segmt_lib.chunk_saver.SaveChunkDataParser()
    response_data = chunk_saver.do_execute(
        infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data')),
        document_data_json.get('context_data'), config_data_json.get('processor_input_config'))
    infy_dpp_segmt_lib.common.FileUtil.save_to_json(
        output_file_path, response_data.dict())
    assert response_data.context_data.get('save_chunk_data') is not None
