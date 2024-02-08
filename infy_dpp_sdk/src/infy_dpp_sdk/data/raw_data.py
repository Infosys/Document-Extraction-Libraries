# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import Any, List

from pydantic import BaseModel


class ContentData(BaseModel):
    content_type: str = None
    content: str = None
    content_bbox: List[float] = None
    bbox_format: str = None
    confidence_pct: int = None
    page: int = None
    sequence: int = -1


class ClassData(BaseModel):
    class_class: str = None
    class_type: str = None
    confidence_pct: int = None


class KeyValueData(BaseModel):
    key: ContentData = None
    value: ContentData = None
    pair_confidence_pct: int = None
    key_classes: List[ClassData] = None
    value_classes: List[ClassData] = None


class CellData(BaseModel):
    page: int = None
    handwritten: bool = None
    confidence_pct: int = None
    row_index: int = None
    row_span: int = None
    column_index: int = None
    column_span: int = None
    text: str = None
    bbox: List[float] = None
    is_header: bool = None


class Table(BaseModel):
    cells: List[CellData] = None


class TableData(BaseModel):
    name: str = None
    text: str = None
    confidence_pct: int = None
    text_list: List[Any] = None
    page: int = None
    table: Table = None
    table_bbox: List[float] = None


class RawData(BaseModel):
    table_data: List[TableData] = None
    key_value_data: List[KeyValueData] = None
    heading_data: List[ContentData] = None
    page_header_data: List[ContentData] = None
    page_footer_data: List[ContentData] = None
    segment_data: List[ContentData] = None
    other_data: List[ContentData] = None
