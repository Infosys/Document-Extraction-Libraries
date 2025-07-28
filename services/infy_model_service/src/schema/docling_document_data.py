# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class TableDataHtml(BaseModel):
    """Class for storing table data html"""
    table_ref: str
    table_data_html: str


class BaseDoclingDocumentData(BaseModel):
    """Base class for storing docling response details"""
    document_data: dict
    document_data_html: str
    table_data_html: list[TableDataHtml]


class DoclingDocumentData(BaseDoclingDocumentData):
    """Class for storing docling response details"""
