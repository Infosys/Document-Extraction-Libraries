"""Module to extract table data from the input image file using Bordered Table Extractor"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import infy_fs_utils
import infy_table_extractor as ite
from infy_object_detector.schema.table_data import (BaseTableConfigData, BaseTableRequestData,
                                                    BaseTableResponseData, MessageData, TableData, TableHtmlData, CellData)
from ..interface import ITableStructureRecogniserProvider


class BorderedTableTsrProviderConfigData(BaseTableConfigData):
    """"Config data for Bordered Table Extractor"""
    ocr_engine_exe_dir_path: str = None
    ocr_engine_model_dir_path: str = None
    temp_folder_path: str = None
    config_param_dict: dict = {
        'custom_cells': [{'rows': [], 'columns': []}],
        'col_header': {'use_first_row': True, 'values': []},
        'deskew_image_reqd': False,
        'auto_detect_border': False,
        'image_cell_cleanup_reqd': True,
        'output': {
            'path': None,
            'format': None
        },
        'rgb_line_skew_detection_method': [ite.interface.RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT]
    }


class BorderedTableTsrProviderRequestData(BaseTableRequestData):
    """"Request data for Bordered Table Extractor"""
    bbox: list


class BorderedTableTsrProvider(ITableStructureRecogniserProvider):
    """Bordered Table TSR Provider class"""

    def __init__(self, config_data: BorderedTableTsrProviderConfigData) -> None:

        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        self._config_data = config_data

        provider = None
        if config_data.model_path:
            provider = ite.bordered_table_extractor.providers.TesseractDataServiceProvider(
                config_data.model_path)
        else:
            provider = ite.bordered_table_extractor.providers.InfyOcrEngineDataServiceProvider(
                config_data.ocr_engine_exe_dir_path, config_data.ocr_engine_model_dir_path)

        self.__bordered_table_extractor = ite.bordered_table_extractor.BorderedTableExtractor(
            provider, provider, self._config_data.temp_folder_path, debug_mode_check=True)

    def extract_table_data(self, table_request_data: BorderedTableTsrProviderRequestData) -> BaseTableResponseData:
        """Extract table data from the input image file"""
        image_file_path = table_request_data.image_file_path
        response = None
        try:
            self.__logger.info(
                "TSR method : %s", self._config_data.config_param_dict.get(
                    'line_detection_method'))
            self.__logger.info(
                "Extraction started for file : %s", image_file_path)

            bte_result = self.__bordered_table_extractor.extract_all_fields(
                image_file_path, within_bbox=table_request_data.bbox, config_param_dict=self._config_data.config_param_dict)
            self.__logger.debug(bte_result)
            response = self.__convert_to_base_table_response(bte_result)
            self.__logger.info(
                "Extraction completed for file : %s", image_file_path)
        except Exception as e:
            self.__logger.error("Error : %s", str(e))
            raise e
        return response

    def __convert_to_base_table_response(self, bte_result) -> BaseTableResponseData:
        """Converts the Bordered Table Extractor result to BaseTableResponseData"""
        table_value = []
        no_of_rows = 0
        no_of_columns = 0
        cell_data_list = []
        bbox = []
        cell_data_html = ""
        debug_path = ""
        fields = bte_result.get('fields')
        error = bte_result.get('error')
        if fields and len(fields) > 0:
            table_value = fields[0].get('table_value')
            if table_value:
                if isinstance(table_value[0], dict):
                    no_of_rows = len(table_value)
                    no_of_columns = len(table_value[0].keys()) if table_value and len(
                        table_value) > 0 else 0
                    cell_data_list = self.__populate_cell_data(table_value)
                    cell_data_html = self.__get_html_table_data(table_value)
                else:
                    error = "Table value is not in expected format"
            provider_bbox = fields[0].get('table_value_bbox')
            bbox = [provider_bbox[0], provider_bbox[1], provider_bbox[2] +
                    provider_bbox[0], provider_bbox[3] + provider_bbox[1]]
            debug_path = fields[0].get('debug_path')
        message_data = []
        if error:
            message_data.append(MessageData(
                message_type="error",
                message=error
            ))
        else:
            message_data.append(MessageData(
                message_type="info",
                message="Successfully extracted table data"
            ))
        table_data = TableData(
            no_of_rows=no_of_rows,
            no_of_columns=no_of_columns,
            title="",
            bbox=bbox,
            cell_data=cell_data_list,
            message_data=message_data,
            debug_path=debug_path
        )
        table_html_data = TableHtmlData(
            title="",
            cell_data_html=cell_data_html,
            message_data=message_data
        )
        base_table_response = BaseTableResponseData(
            table_data=[table_data],
            table_html_data=[table_html_data])
        return base_table_response

    def __populate_cell_data(self, table_value):
        cell_data_list = []
        # Add headers
        headers = list(table_value[0].keys())
        for col_index, header in enumerate(headers):
            cell_data_list.append(CellData(
                type="columnHeader",
                row_index=0,
                column_index=col_index,
                row_span=1,
                column_span=1,
                content=header,
                bbox=[]
            ))

        # Add rows
        for row_index, row in enumerate(table_value, start=1):
            for col_index, (key, value) in enumerate(row.items()):
                cell_data_list.append(CellData(
                    type="data",
                    row_index=row_index,
                    column_index=col_index,
                    row_span=1,
                    column_span=1,
                    content=value,
                    bbox=[]
                ))

        return cell_data_list

    def __get_html_table_data(self, table_value):
        html = ""
        # Start HTML table
        html = '<table border="1">'

        # Add headers
        headers = table_value[0].keys()
        html += '  <tr>'
        for header in headers:
            html += f'    <th>{header}</th>'
        html += '  </tr>'

        # Add rows
        for row in table_value:
            html += '  <tr>'
            for cell in row.values():
                html += f'    <td>{cell}</td>'
            html += '  </tr>'

        # End HTML table
        html += '</table>'

        return html
