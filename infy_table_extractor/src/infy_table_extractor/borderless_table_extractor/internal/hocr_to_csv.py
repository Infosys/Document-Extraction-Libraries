# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
import os
from lxml import etree, html
import pandas as pd


class HOCRToCSV:
    @classmethod
    def convert(cls, hocr_file_path, output_file_path, processing_msg=[]):
        p1 = re.compile(r'bbox((\s+\d+){4})')
        p2 = re.compile(r'baseline((\s+[\d\.\-]+){2})')
        df = pd.DataFrame()
        (_, hocr_file_name_with_ext) = os.path.split(
            hocr_file_path)
        (hocr_file_name_only, _) = os.path.splitext(hocr_file_name_with_ext)
        hocr = etree.parse(hocr_file_path, html.XHTMLParser())
        df = cls.__extract_xpath(
            hocr, '//*[@class="ocr_line"]', df, p1, p2, hocr_file_name_only)
        df = cls.__extract_xpath(
            hocr, '//*[@class="ocr_textfloat"]', df, p1, p2, hocr_file_name_only)
        df = cls.__extract_xpath(
            hocr, '//*[@class="ocr_header"]', df, p1, p2, hocr_file_name_only)
        df.to_csv(output_file_path, header=None)
        processing_msg.append(
            f"Hocr file is converted as CSV and path is {output_file_path}")

    @classmethod
    def __extract_xpath(cls, hocr, xpath_str, df, p1, p2, hocrfilename):
        for line in hocr.xpath(xpath_str):
            linebox = p1.search(line.attrib['title']).group(1).split()
            try:
                baseline = p2.search(line.attrib['title']).group(1).split()
            except AttributeError:
                baseline = [0, 0]
            linebox = [float(i) for i in linebox]
            baseline = [float(i) for i in baseline]
            xpath_elements = './/*[@class="ocrx_word"]'
            if (not (line.xpath('boolean(' + xpath_elements + ')'))):
                # if there are no words elements present,
                # we switch to lines as elements
                xpath_elements = '.'
            for word in line.xpath(xpath_elements):
                rawtext = word.text_content().strip()
                if rawtext == '':
                    continue
                box = p1.search(word.attrib['title']).group(1).split()
                box = [float(i) for i in box]
                row = pd.Series([hocrfilename, rawtext, box])
                df = pd.concat([df, row.to_frame().T], ignore_index=True)
        return df
