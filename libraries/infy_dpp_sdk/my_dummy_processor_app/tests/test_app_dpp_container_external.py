# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import sys
import os
import pytest
from app_dpp_container_external import App

STORAGE_ROOT_PATH = f"C:/temp/unittest/my_dummy_processor_app/{__name__}/STORAGE"
INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_input_config.json'
PARALLEL_INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2p_input_config.json'


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        [os.path.basename(INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ["*", f"{SAMPLE_ROOT_PATH}/input", f"{STORAGE_ROOT_PATH}/data/input"],
        [os.path.basename(PARALLEL_INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)


def test_app_dpp_container_full_pipeline():
    """Test case for app_dpp_container to execute first processor of pipeline"""

    PROCESSOR_LIST = ['document_downloader', 'content_extractor',
                      'attribute_extractor', 'document_uploader']
    prev_response_file_path = ''
    # INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_cloud_input_config.json'
    # Comment below when running using cli command
    # and set DPP_STORAGE_ROOT_URI=s3://docwb-engg/local ,# DPP_STORAGE_SERVER_URL during runtime.
    # or  DPP_STORAGE_ROOT_URI=file://C:/temp/unittest/my_dummy_processor_app//tests.test_app_dpp_container_external/STORAGE

    os.environ['DPP_STORAGE_ROOT_URI'] = f"file://{STORAGE_ROOT_PATH}"
    app = App()
    for processor_name in PROCESSOR_LIST:
        sys.argv = ['<leave empty>',
                    '--processor_name', processor_name,
                    '--input_config_file_path', INPUT_CONFIG_FILE_PATH,
                    '--prev_proc_response_file_path', prev_response_file_path]
        prev_response_file_path = app.do_processing()
        assert prev_response_file_path is not None


def test_app_dpp_container_full_pipeline_2():
    """Test case for app_dpp_container to execute parallel processor of pipeline"""

    PROCESSOR_LIST = ['document_downloader', 'content_extractor',
                      'attribute_extractor', 'document_uploader']
    prev_response_file_path = ''
    prev_proc_response_file_path_2 = ''
    prev_proc_response_file_path_3 = ''
    # INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_cloud_input_config.json'
    # Comment below when running using cli command
    # and set DPP_STORAGE_ROOT_URI=s3://docwb-engg/local ,# DPP_STORAGE_SERVER_URL during runtime.
    # or  DPP_STORAGE_ROOT_URI=file://C:/temp/unittest/my_dummy_processor_app//tests.test_app_dpp_container_external/STORAGE

    os.environ['DPP_STORAGE_ROOT_URI'] = f"file://{STORAGE_ROOT_PATH}"
    app = App()
    # initial_arg = sys.argv
    for processor_name in PROCESSOR_LIST:
        sys.argv = ['<leave empty>',
                    '--processor_name', processor_name,
                    '--input_config_file_path', INPUT_CONFIG_FILE_PATH,
                    '--prev_proc_response_file_path', prev_response_file_path,
                    '--prev_proc_response_file_path_2', prev_proc_response_file_path_2,
                    '--prev_proc_response_file_path_3', prev_proc_response_file_path_3]
        app_args = sys.argv
        # app_args = [
        #     '--processor_name', processor_name,
        #     '--input_config_file_path', INPUT_CONFIG_FILE_PATH,
        #     '--prev_proc_response_file_path_0', prev_response_file_path,
        #     '--prev_proc_response_file_path_1', prev_response_file_path,
        #     '--prev_proc_response_file_path_2', prev_response_file_path
        # ]
        # sys.argv = initial_arg + app_args
        # sys.argv = app_args
        print("sys.argv", sys.argv)
        print("len(sys.argv)", len(sys.argv))
        prev_response_file_path = app.do_processing()
        if processor_name == 'attribute_extractor':
            sys.argv = app_args
            prev_proc_response_file_path_2 = app.do_processing()
            sys.argv = app_args
            prev_proc_response_file_path_3 = app.do_processing()
        assert prev_response_file_path is not None


def test_app_dpp_container_full_pipeline_3():
    """Test case for app_dpp_container to execute parallel processor of pipeline"""

    PROCESSOR_LIST = ["document_downloader", "content_extractor",
                      "attribute_extractorA", "attribute_extractorB", "document_uploader"]
    prev_response_file_path = ''
    # prev_proc_response_file_path_2 = ''
    # prev_proc_response_file_path_3 = ''
    attribute_extractorA_response_file_path = ''
    attribute_extractorB_response_file_path = ''
    os.environ['DPP_STORAGE_ROOT_URI'] = f"file://{STORAGE_ROOT_PATH}"
    app = App()
    for processor_name in PROCESSOR_LIST:
        if processor_name == 'document_uploader':
            sys.argv = ['<leave empty>',
                        '--processor_name', processor_name,
                        '--input_config_file_path', PARALLEL_INPUT_CONFIG_FILE_PATH,
                        '--prev_proc_response_file_path', attribute_extractorA_response_file_path,
                        '--prev_proc_response_file_path_2', attribute_extractorB_response_file_path,
                        ]
        else:
            sys.argv = ['<leave empty>',
                        '--processor_name', processor_name,
                        '--input_config_file_path', PARALLEL_INPUT_CONFIG_FILE_PATH,
                        '--prev_proc_response_file_path', prev_response_file_path,
                        ]
        print("sys.argv", sys.argv)
        print("len(sys.argv)", len(sys.argv))

        if processor_name == 'attribute_extractorA':
            attribute_extractorA_response_file_path = app.do_processing()
        elif processor_name == 'attribute_extractorB':
            attribute_extractorB_response_file_path = app.do_processing()
        else:
            prev_response_file_path = app.do_processing()
        assert prev_response_file_path is not None
