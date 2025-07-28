# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import infy_table_extractor as ite


# environment variables
TESSERACT_PATH = os.environ['TESSERACT_PATH']

TEMP_FOLDER_PATH = os.path.abspath('.\\data\\temp')
OUTPUT_FOLDER_PATH = os.path.abspath('.\\data\\output')
INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\infy_table_extractor\\borderless_table"
input_file = f"{UNIT_TEST_DATA_LOCATION}\\sample_2_lite\\GE - Case 2120609_1_1.jpg"


def __create_new_instance():

    tesseract_provider = ite.borderless_table_extractor.providers.TesseractDataServiceProvider(
        TESSERACT_PATH)
    extractor_obj = ite.borderless_table_extractor.BorderlessTableExtractor(
        TEMP_FOLDER_PATH,
        token_rows_cols_provider=tesseract_provider,
        token_detection_provider=tesseract_provider,
        token_enhance_provider=tesseract_provider,
        pytesseract_path=TESSERACT_PATH, debug_mode_check=False
    )

    if not os.path.exists(TEMP_FOLDER_PATH):
        os.makedirs(TEMP_FOLDER_PATH)

    if not os.path.exists(OUTPUT_FOLDER_PATH):
        os.makedirs(OUTPUT_FOLDER_PATH)

    return extractor_obj


def test_extract_native_pdf_1():
    """Native pdf test method 1"""
    extractor_obj = __create_new_instance()
    input_pdf = os.path.abspath("./data/samples/infosys_q1-2022.pdf")
    input_img = os.path.abspath(
        "./data/samples/infosys_q1-2022.pdf_files/1.jpg")
    response_dict = extractor_obj.extract_all_fields(
        input_img, file_data_list=[
            {"path": input_pdf, "pages": [1]}],
        config_param_dict={"ocr_tool_settings": {'tesseract': {'psm': '12'}},
                           "is_virtual_table_mode": True})
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_native_pdf_2():
    """with hocr file data"""
    extractor_obj = __create_new_instance()
    input_pdf = os.path.abspath("./data/samples/infosys_q1-2022.pdf")
    input_img = os.path.abspath(
        "./data/samples/infosys_q1-2022.pdf_files/1.jpg")
    # if the file not exist then remove from file_data_list and run.
    img_ocr_file = os.path.abspath("./data/temp/1.jpg/1_vtm.hocr")
    nativepdf_provider = ite.borderless_table_extractor.providers.NativePdfDataServiceProvider()
    extractor_obj.set_token_enchance_provider(nativepdf_provider)
    response_dict = extractor_obj.extract_all_fields(
        input_img, file_data_list=[{"path": img_ocr_file, "pages": [1]}, {
            "path": input_pdf, "pages": [1]}],
        config_param_dict={"is_virtual_table_mode": True})
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_se():
    """Test method"""
    extractor_obj = __create_new_instance()
    for i in range(1, 2):
        input_file_1 = f"{UNIT_TEST_DATA_LOCATION}\\sample_3\\4512021882_s{i}-0.jpg"
        response_dict = extractor_obj.extract_all_fields(
            input_file_1, config_param_dict={"is_virtual_table_mode": True})
        assert response_dict["error"] is None and len(
            [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_cs_1():
    """Test method"""
    extractor_obj = __create_new_instance()
    input_file_1 = f"{UNIT_TEST_DATA_LOCATION}\\sample_1\\C&S bkup_6_1.jpg"
    response_dict = extractor_obj.extract_all_fields(
        input_file_1, config_param_dict={"is_virtual_table_mode": True,
                                         "col_header": {"use_first_row": False}})
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_in():
    """Test method"""
    extractor_obj = __create_new_instance()
    for i in range(2, 3):
        input_file_1 = f"{UNIT_TEST_DATA_LOCATION}\\sample_4\\6200077846_RPA_FEB_2020_{i}.jpg"
        response_dict = extractor_obj.extract_all_fields(
            input_file_1, config_param_dict={"is_virtual_table_mode": True})
        assert response_dict["error"] is None and len(
            [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_ge_1():
    """Test method"""
    extractor_obj = __create_new_instance()
    for i in range(19, 20):
        input_file_1 = f"{UNIT_TEST_DATA_LOCATION}\\sample_2\\ge_2120609_{i}_1.jpg"
        response_dict = extractor_obj.extract_all_fields(
            input_file_1, config_param_dict={"is_virtual_table_mode": True})
        assert response_dict["error"] is None and len(
            [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_custom_table_organise_prop():
    """Ext to Html test method"""
    extractor_obj = __create_new_instance()
    table_organization_dict = json.loads(
        open(UNIT_TEST_DATA_LOCATION + "/sample_2_lite/text_processing_config.txt", "r",
             encoding='utf-8').read())
    config_param_dict = {'table_organization_dict': table_organization_dict}
    response_dict = extractor_obj.extract_all_fields(
        input_file, config_param_dict=config_param_dict)
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0


def test_extract_custom_cells():
    """Ext to Html test method 1"""
    extractor_obj = __create_new_instance()
    config_param_dict = {"custom_cells": [{'rows': [':5'], 'columns': ['0:']}],
                         "is_virtual_table_mode": False}
    response_dict = extractor_obj.extract_all_fields(
        input_file, config_param_dict=config_param_dict)
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0


# As discussed, the output path is not recommended and API should return only JSON.
# Hence, commenting below test method.
# def test_extract_comp_files():
#     """diff class image compattibility test"""
#     source_img_path = f"{UNIT_TEST_DATA_LOCATION}\\table_img_class"
#     base_html_path = f"{source_img_path}\\baseline"

#     # for getting the input image in a list
#     files, base_html_file, output_html_file, file_ext = [
#     ], [], [], ['*.jpg', '*.png', '*.jpeg']
#     for ext in file_ext:
#         files.extend(glob.glob(f"{source_img_path}/{ext}", recursive=True))

#     # for getting baseline html file list'''
#     for html_files in glob.glob(base_html_path+"**/*.html", recursive=True):
#         base_html_file.append(html_files)

#     for input_img_file in files:
#         config_param_dict = {"is_virtual_table_mode": True, 'output': {
#             'path': OUTPUT_FOLDER_PATH, 'format': ""}}
#         response_dict = extractor_obj.extract_all_fields(
#             input_img_file, config_param_dict=config_param_dict)
#         assert response_dict["fields"][0]['error'] is None

#     # for getting output html  file list'''
#     for out_html_files in glob.glob(OUTPUT_FOLDER_PATH+"**/*.html", recursive=True):
#         output_html_file.append(out_html_files)

#     # Checking if the output file is same as baseline
#     for outfile in output_html_file:
#         outfilename = os.path.basename(outfile)
#         for base_html in base_html_file:
#             base_file_name = os.path.basename(base_html)
#             if outfilename == base_file_name:
#                 flag = True
#                 with open(outfile) as out, open(base_html) as base:
#                     out_read = out.read()
#                     base_read = base.read()
#                     if out_read != base_read:
#                         flag = False
#                 assert flag is True
#                 break


def test_multiline_extract():
    """Multiline extraction test case"""
    extractor_obj = __create_new_instance()
    multiline_input_file = f"{UNIT_TEST_DATA_LOCATION}\\table_img_class\\bl_simple_multiline_1.png"
    config_param_dict = {"is_virtual_table_mode": True}
    response_dict = extractor_obj.extract_all_fields(
        multiline_input_file, config_param_dict=config_param_dict)
    assert response_dict["error"] is None and len(
        [x for x in response_dict['fields'] if x.get("error")]) == 0
