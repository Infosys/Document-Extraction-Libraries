# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional, Literal
from pydantic import BaseModel


class CellData(BaseModel):
    """Class for cell data"""
    type: str
    row_index: int
    column_index: int
    row_span: int
    column_span: int
    content: str
    bbox_format: str = "X1,Y1,X2,Y2"
    bbox: list[float]


class MessageData(BaseModel):
    """Class for messages"""
    message_type: Literal['error', 'warn', 'info']
    message: str


class TableData(BaseModel):
    """Class for table data """
    no_of_rows: int = None
    no_of_columns: int = None
    title: Optional[str] = None
    td_confidence_pct: Optional[float] = -1.0
    bbox_format: str = "X1,Y1,X2,Y2"
    bbox: list[float] = None
    cell_data: List[CellData] = None
    message_data: List[MessageData] = None
    tsr_confidence_pct: Optional[float] = -1.0
    debug_path: Optional[str] = None


class TableHtmlData(BaseModel):
    """Class for table html data"""
    title: Optional[str] = None
    cell_data_html: str = None
    message_data: List[MessageData] = None


class YoloxTdRequestData(BaseModel):
    """Yolox table request data class"""
    image_file_path: str


class YoloxTdResponseData(BaseModel):
    """Yolox table response data class"""
    table_data: List[TableData]
    table_html_data: List[TableHtmlData] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
