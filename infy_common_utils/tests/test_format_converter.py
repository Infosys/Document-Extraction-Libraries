# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import tempfile
import os
import shutil
import infy_common_utils.format_converter as format_converter
from infy_common_utils.format_converter import FormatConverter, ConvertAction


format_converter.format_converter_jar_home = os.environ[
    'FORMAT_CONVERTER_HOME']


def test_convert_pdf2txt_1():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
    config_param_dict = {
        "pages": [1]
    }

    # PDF_TO_TXT
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_TXT, config_param_dict=config_param_dict)

    assert result == ('Infosys Integrated Annual Report 2022-23 Infosys Integrated Annual Report 2022-2328 29\nBusiness highlights\nPerformance overview\nDividend per share (in ?)\n34.0\n9.7% growth Y-o-Y\nRevenues\n? 1,46,767cr\n20.7% growth Y-o-Y \n15.4% CC growth Y-o-Y\nOperating margin\n21.0%\nRobust operating margin\nInfosys achieved industry-\nleading revenue growth of \n15.4% with healthy operating \nmargin of 21.0% for fiscal \n2023. Our ESG Vision 2030 and \nambitions continue to drive \nvalue for all our stakeholders.\nCarbon offset programs\n2,40,000+\nRural families continue to benefit\nDigital revenues \n(as a % of total revenue)\n62.2%\n25.6% CC growth Y-o-Y\nFree cash(1)\n? 20,443cr\n FCF conversion at 84.8% of net profit\nConsolidated cash and \ninvestments(2)\n? 31,286cr\nContinue to main strong \nliquidity\xa0position\nBuyback completed\n? 9,300cr\nat an average price of ? 1,539.06\nReturn on equity\n31.2%\nImproved by 2.1% over \nthe\xa0last fiscal\nBasic earnings per share\n(par value of ? 5 each)\n57.63\n9.7% growth Y-o-Y\nNumber of US$ 50 million + clients\n75\nStrong client metrics with increase  \nof 11 clients Y-o-Y\nIn ? crore, except per equity share data FY 2023 FY 2022 FY 2021 FY 2020 FY 2019\nRevenues(1) 1,46,767 1,21,641 1,00,472 90,791 82,675 \nNet profit(1)(2) 24,095 22,110 19,351 16,594 15,404\nBasic earnings per share (in ?)(1) 57.63 52.52 45.61 38.97 35.44 \nMarket capitalization 5,92,394 8,02,162 5,82,880 2,73,214 3,24,448 \nIn US$ million, except per equity share data FY 2023 FY 2022 FY 2021 FY 2020 FY 2019\nRevenues(1) 18,212 16,311 13,561 12,780 11,799 \nNet profit(1)(2) 2,981 2,963 2,613 2,331 2,199\nBasic earnings per share (in ?)(1) 0.71 0.70 0.62 0.55 0.51 \nMarket capitalization 72,351 104,706 79,760 34,966 47,614 \nNotes:\n(1) Based on IFRS consolidated financial statements\n(2) Attributable to owners of the Company\nKey trends\nNote:\n(1) Free cash flow is defined as net cash provided by operating activities less capital expenditure as per the Consolidated Statement of Cash Flows \nprepared under IFRS.\n(2) Comprise cash and cash equivalents, current and non-current investments excluding investments in unquoted equity and preference shares, and others.\nLarge deal TCV\n(Total contract value in US$ billion)\n$9.8b\nSustained momentum in large \ndeal\xa0wins continues\nWomen employees\n39.4%\nSteady progress towards \ngender\xa0diversity goals\nDigital skilling\n8.5mn\nPeople are a part of our digital \nskilling\xa0initiatives\nTech for Good\n114mn +\nLives empowered via our Tech for \nGood solutions in e-governance, \neducation and healthcare\nCarbon neutrality\nCarbon neutral for \n4 years in a row\nScope 1, 2 and 3 emissions ~50,000\nFresh graduates hired globally\n\n')


def test_convert_pdf2json_1():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
    config_param_dict = {
        "pages": [1],
        "bboxes": [[185, 160, 950, 283]],
        "page_dimension": {
            "width": 5100,
            "height": 3299
        }
    }
    # PDF_TO_JSON
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_JSON, config_param_dict=config_param_dict)
    print(result)
    assert result == [{'pageNum': '1', 'regions': [
        {'name': 'bbox1',
         'text':  ('Business highlights\r\nPerformance overview'),
         'bbox': [185, 160, 950, 283]}], 'pageText': ''}]


def test_convert_pdf2txt_2():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
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
    from_file = os.path.abspath("./data/page-14-17.pdf")
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
    from_file = os.path.abspath("./data/page-14-17.pdf")
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
        assert (
            ex.args[0] == "Could not find any jar file of format 'infy-format-converter-*.jar' at provided path 'None'")


def test_convert_pdf2mulpdf_1():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
    config_param_dict = {
        "pages": [1]
    }
    # PDF_TO_MULTIPDF
    result, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_MULTIPDF, config_param_dict=config_param_dict)
    print(result)
    assert len(result) > 0


def test_convert_pdfrotate_1():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
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
    from_file = os.path.abspath("./data/page-14-17.pdf")
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


def test_images_from_pdf():
    """Test method"""
    from_file = os.path.abspath("./data/page-14-17.pdf")
    to_dir = tempfile.TemporaryDirectory().name
    config_param_dict = {
        "to_dir": to_dir,
        "saveresource": True
    }
    # PDF_TO_IMAGE_BBOX
    output_files, _ = FormatConverter.execute(
        from_file, convert_action=ConvertAction.PDF_TO_IMAGE_BBOX, config_param_dict=config_param_dict)

    print(output_files)
    assert len(output_files) is not None
