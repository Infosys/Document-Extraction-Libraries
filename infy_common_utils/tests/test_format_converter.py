# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import tempfile
import os
import glob
import shutil
import infy_common_utils.format_converter as format_converter
from infy_common_utils.format_converter import FormatConverter, ConvertAction

GITHUB_TEMPLATE_LOCATION = ("C:\\INFYGITHUB\\ainautosolutions\\workbenchlibraries\\"
                            "\\stackXtractor\\unit_test_data\\infy_common_utils")

format_converter.format_converter_jar_home = os.environ[
    'FORMAT_CONVERTER_HOME']


def test_convert_aod_pdf2json_1():
    """Test method"""
    file_dir = f"{GITHUB_TEMPLATE_LOCATION}\\art-of-dissolution-general-prior"
    from_file = f"{file_dir}\\Art of Dissolution General Prior - ABC Corporation.pdf"
    config_param_dict = {
        "pages": [1],
        "bboxes": [[170, 833, 890, 165]],
        "page_dimension": {
            "width": 2550,
            "height": 3299
        }
    }
    # PDF_TO_JSON
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_JSON, config_param_dict=config_param_dict)
    assert result == [
        {"pageNum": "1",
         "regions": [
             {"name": "bbox1",
              "text": "The name of the corporation is:",
              "bbox": [170, 833, 890, 165]
              }],
         "pageText": ""}
    ]


def test_convert_aod__pdf2txt_2():
    """Test method"""
    file_dir = f"{GITHUB_TEMPLATE_LOCATION}\\art-of-dissolution-general-prior"
    from_file = f"{file_dir}\\Art of Dissolution General Prior - ABC Corporation.pdf"
    config_param_dict = {
        "pages": [1]
    }

    # PDF_TO_TXT
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_TXT, config_param_dict=config_param_dict)

    assert result == ("4. No debt of the corporation remains unpaid.\n""1. The name of the corporation is:\n"
                      "2. The date of its incorporation was:\na) None of the corporation's shares has been issued.\n"
                      "3. Check one or both of the following boxes:\nb) The corporation has not commenced business.\n"
                      "5. If shares were issued, the net assets remaining after winding up have been distributed "
                      "to the shareholders.\n6. A majority of the  (     incorporators  OR       initial directors) "
                      "authorized the dissolution.\n(choose one)\nSecretary of State use only\n"
                      "Printed Name:\nSignature:\nRevised 12/2018\n incorporator  initial director\n(mm/dd/yyyy)\n"
                      "(choose one)\nARTICLES OF DISSOLUTION\n(General Business and Professional Corporations)\n"
                      "(prior to issuing shares or commencing business)\nTitle 30, Chapters 21 and 29, Idaho Code\n"
                      "Base Filing fee: $0.00 + $20.00 for manual processing (form must be typed).\n\n")


def test_convert_assa_abloy__pdf2json_1():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    config_param_dict = {
        "pages": [1],
        "bboxes": [[143, 592, 1094, 194]],
        "page_dimension": {
            "width": 2550,
            "height": 3299
        }
    }
    # PDF_TO_JSON
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_JSON, config_param_dict=config_param_dict)
    print(result)
    assert result == [{'pageNum': '1', 'regions': [
        {'name': 'bbox1',
         'text':  ('PRODUCER\r\nAon Risk Services South, Inc.\r\nCharlotte NC Office\r\n'
                   '1111 Metropolitan Avenue,  Suite 400\r\nCharlotte NC 28204 USA'),
         'bbox': [143, 592, 1094, 194]}], 'pageText': ''}]


def test_convert_assa_abloy_pdf2txt_2():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    config_param_dict = {
        "pages": [1],
    }
    # PDF_TO_TXT
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_TXT, config_param_dict=config_param_dict)
    print(result)
    assert True if result else False


def test_convert_pdf_to_image_all_pages():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    to_dir = tempfile.TemporaryDirectory().name
    config_param_dict = {
        "to_dir": to_dir,
        "dpi": 100
    }
    # PDF_TO_IMAGE
    img_files, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_IMAGE, config_param_dict=config_param_dict)

    print(img_files)
    for img_file in img_files:
        assert os.path.isfile(img_file)


def test_convert_pdf_to_image_one_page():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    to_dir = tempfile.TemporaryDirectory().name
    config_param_dict = {
        "pages": [1],
        "to_dir": to_dir
    }
    # PDF_TO_IMAGE
    img_files, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_IMAGE, config_param_dict=config_param_dict)

    print(img_files)

    assert len(img_files) == 1

    for img_file in img_files:
        assert os.path.isfile(img_file)


def test_invalid_format_converter_path():
    """Test method"""
    format_converter.format_converter_jar_home = None
    try:
        FormatConverter.execute(
            None, convert_action=ConvertAction.PDF_TO_IMAGE, config_param_dict={})

    except Exception as ex:
        assert(
            ex.args[0] == "Could not find any jar file of format 'infy-format-converter-*.jar' at provided path 'None'")


def test_convert_assa_abloy_pdf2mulpdf_1():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    config_param_dict = {
        "pages": [1]
    }
    # PDF_TO_MULTIPDF
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_MULTIPDF, config_param_dict=config_param_dict)
    print(result)
    assert len(result) > 0


def test_convert_assa_abloy_pdfrotate_1():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    config_param_dict = {
        "pages": [1],
        "angles": [90]
    }
    from_file = shutil.copyfile(from_file, f"{from_file}_copy.pdf")
    # ROTATE_PDF_PAGE
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.ROTATE_PDF_PAGE, config_param_dict=config_param_dict)
    print(result)
    assert len(result) > 0


def test_convert_pdf_to_text_bbox():
    """Test method"""
    from_file = glob.glob(
        f"{GITHUB_TEMPLATE_LOCATION}\\aon\\Assa Abloy\\Assa Abloy America_19052015240693*.pdf")[0]
    to_dir = tempfile.TemporaryDirectory().name
    config_param_dict = {
        "to_dir": to_dir,
        "plotbbox": False,
    }
    # PDF_TO_TEXT_BBOX
    output_files, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_TEXT_BBOX, config_param_dict=config_param_dict)

    print(output_files)

    if config_param_dict['plotbbox']:
        assert len(output_files) == 2
    else:
        assert len(output_files) == 1

    for img_file in output_files:
        assert os.path.isfile(img_file)
