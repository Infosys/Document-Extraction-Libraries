"""Module to extract table data from the input image file using API call to model service"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import requests
import logging
import infy_fs_utils
from ..interface import ITableDetectorProvider
from infy_object_detector.schema.table_data import (BaseTableConfigData, BaseTableRequestData,
                                                    BaseTableResponseData, MessageData, TableData, TableHtmlData, CellData)

RETRIVE_ENDPOINT = "/retrieve"
EXTRACT_ENDPOINT = "/extract"


class DoclingTableTdTsrProviderConfigData(BaseTableConfigData):
    """Docling Table TD TSR Provider Config Data"""
    model_service_url: str = None
    is_table_html_view: bool = False


class DoclingTableTdTsrProviderRequestData(BaseTableRequestData):
    """Docling Table TD TSR Provider Request Data"""


class DoclingTableTdTsrProviderResponseData(BaseTableResponseData):
    """Docling Table TD TSR Provider Response Data"""
    image_width: int = None
    image_height: int = None


class DoclingTableTdTsrProvider(ITableDetectorProvider):
    def __init__(self, config_data: DoclingTableTdTsrProviderConfigData) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        self.__model_extractor_service_url = config_data.model_service_url+EXTRACT_ENDPOINT
        self.__model_retriever_service_url = config_data.model_service_url+RETRIVE_ENDPOINT
        self.__is_table_html_view = config_data.is_table_html_view

    def detect_table(self, request_data: DoclingTableTdTsrProviderRequestData) -> DoclingTableTdTsrProviderResponseData:
        image_file_path = request_data.image_file_path
        result = None
        try:
            with open(image_file_path, 'rb') as f:
                files = {'file': f}
                document_data = requests.post(
                    self.__model_extractor_service_url, files=files, timeout=400)
                document_data = document_data.json()
                table_data_html = {}
                if self.__is_table_html_view:
                    unique_id = document_data.get("unique_id")
                    table_data_html = requests.post(
                        self.__model_retriever_service_url, json={"unique_id": unique_id,
                                                                  "document_html": False,
                                                                  "table_html": True}, timeout=10)
                    table_data_html = table_data_html.json()

                result = self.__convert_to_base_table_response(
                    document_data, table_data_html)
                # result = document_data
        except Exception as e:
            self.__logger.error("Error : %s", str(e))
            raise e

        return result

    def __convert_to_base_table_response(self, document_data, table_data_html) -> DoclingTableTdTsrProviderResponseData:
        response = None
        table_data_list = []
        table_data_html_list = []
        document_data_page_width = document_data.get("document_data").get(
            "pages").get("1").get("size").get("width")
        document_data_page_height = document_data.get("document_data").get(
            "pages").get("1").get("size").get("height")
        document_table_data_list = document_data.get(
            "document_data").get("tables")
        html_tables_list = table_data_html.get("table_data_html", [])

        # for document_table_data in document_table_data_list:
        for index, document_table_data in enumerate(document_table_data_list):
            data = document_table_data.get("data")
            table_data = TableData()
            document_table_data_bbox = document_table_data.get("prov")[
                0].get("bbox")
            table_data.bbox = [
                round(document_table_data_bbox.get("l"), 2),
                round(document_data_page_height -
                      document_table_data_bbox.get("t"), 2),
                round(document_table_data_bbox.get("r"), 2),
                round(document_data_page_height -
                      document_table_data_bbox.get("b"), 2)
            ]
            table_data.no_of_rows = data.get("num_rows")
            table_data.no_of_columns = data.get("num_cols")
            table_data.cell_data = self.__populate_cell_data(
                data.get("table_cells"), document_data_page_height)
            if table_data.cell_data:
                table_data.message_data = MessageData(
                    message_type="info", message="Table data extracted successfully"
                )
            else:
                table_data.message_data = MessageData(
                    message_type="error", message="Table data extraction failed"
                )
            table_html = TableHtmlData()
            if html_tables_list:
                table_html.cell_data_html = html_tables_list[index].get(
                    "table_data_html")
                table_html.message_data = table_data.message_data
                table_data_html_list.append(table_html)
            table_data_list.append(table_data)

        response = DoclingTableTdTsrProviderResponseData(
            image_width=document_data_page_width,
            image_height=document_data_page_height,
            table_data=table_data_list,
            table_html_data=table_data_html_list
        )
        return response

    def __populate_cell_data(self, table_cells, document_data_page_height):
        cell_data_list = []
        for cell in table_cells:
            cell_bbox = cell.get("bbox")
            if cell_bbox:
                cell_bbox = [
                    round(cell_bbox.get("l"), 2),
                    round(document_data_page_height - cell_bbox.get("t"), 2),
                    round(cell_bbox.get("r"), 2),
                    round(document_data_page_height - cell_bbox.get("b"), 2)
                ]
            else:
                cell_bbox = []
            cell_data = CellData(
                type="columnHeader" if cell.get("column_header") else "data",
                row_index=cell.get("start_row_offset_idx"),
                column_index=cell.get("start_col_offset_idx"),
                row_span=cell.get("row_span"),
                column_span=cell.get("col_span"),
                content=cell.get("text"),
                bbox=cell_bbox
            )
            cell_data_list.append(cell_data)

        return cell_data_list
