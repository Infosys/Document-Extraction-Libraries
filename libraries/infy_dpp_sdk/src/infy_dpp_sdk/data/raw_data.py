# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import Any, List

from pydantic import BaseModel


class ContentData(BaseModel):
    """Content data class"""
    content_type: str | None = None
    content: str | None = None
    content_bbox: List[float] | None = None
    bbox_format: str | None = None
    confidence_pct: int | None = None
    page: int | None = None
    sequence: int = -1


class ClassData(BaseModel):
    """Class data class"""
    class_class: str | None = None
    class_type: str | None = None
    confidence_pct: int | None = None


class KeyValueData(BaseModel):
    """Key Value data class"""
    key: ContentData | None = None
    value: ContentData | None = None
    pair_confidence_pct: int | None = None
    key_classes: List[ClassData] | None = None
    value_classes: List[ClassData] | None = None


class CellData(BaseModel):
    """Cell data class"""
    page: int | None = None
    handwritten: bool | None = None
    confidence_pct: int | None = None
    row_index: int | None = None
    row_span: int | None = None
    column_index: int | None = None
    column_span: int | None = None
    text: str | None = None
    bbox: List[float] | None = None
    is_header: bool | None = None


class Table(BaseModel):
    """Table class"""
    cells: List[CellData] | None = None


class TableData(BaseModel):
    """Table data class"""
    name: str | None = None
    text: str | None = None
    confidence_pct: int | None = None
    text_list: List[Any] | None = None
    page: int | None = None
    table: Table | None = None
    table_bbox: List[float] | None = None


class RawData(BaseModel):
    """Raw data class"""
    table_data: List[TableData] | None = None
    key_value_data: List[KeyValueData] | None = None
    heading_data: List[ContentData] | None = None
    page_header_data: List[ContentData] | None = None
    page_footer_data: List[ContentData] | None = None
    segment_data: List[ContentData] | None = None
    other_data: List[ContentData] | None = None
