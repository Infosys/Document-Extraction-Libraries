# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import pdfplumber
import infy_dpp_sdk
import infy_fs_utils

from infy_dpp_content_extractor.common.file_util import FileUtil


class PdfPlumberService:
    def __init__(self):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()

    def get_tables_content(self, from_files_full_path, out_file_full_path) -> list:
        try:
            with pdfplumber.open(from_files_full_path) as pdf:
                all_pages = []

                for page in pdf.pages:
                    page_tables = []
                    table_objects = page.find_tables()
                    tables = page.extract_tables()
                    table_number = 1

                    for table, table_object in zip(tables, table_objects):
                        header = table[0]
                        table_data = [dict(zip(header, row))
                                      for row in table[1:]]
                        page_tables.append({
                            "table_id": f"p{page.page_number}_tb{table_number}",
                            "bbox": table_object.bbox,
                            "data": table_data
                        })
                        table_number += 1

                    page_dict = {
                        "page_number": page.page_number,
                        "page_width": page.bbox[2],
                        "page_height": page.bbox[3],
                        "tables": page_tables
                    }

                    all_pages.append(page_dict)

            # Define the output file path for the entire PDF
            output_file_path = os.path.join(
                out_file_full_path, f"{os.path.basename(from_files_full_path)}_pdfplumber.json")

            FileUtil.save_to_json(output_file_path, all_pages)

            return output_file_path
        except Exception as e:
            self.__logger.error(f"Error in extracting tables from pdf: {e}")
            return []
