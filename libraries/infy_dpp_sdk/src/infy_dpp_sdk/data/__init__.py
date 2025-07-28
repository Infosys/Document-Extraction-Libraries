# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pydantic

if pydantic.__version__.startswith("1."):
    from ._v1.document_data import DocumentData
    from ._v1.message_data import MessageData
    from ._v1.message_item_data import (
        MessageItemData, MessageTypeEnum, MessageCodeEnum)
    from ._v1.meta_data import MetaData
    from ._v1.page_data import PageData
    from ._v1.processor_response_data import ProcessorResponseData
    from ._v1.standard_data import StandardData
    from ._v1.value_data import ValueData
    from ._v1.extracted_data import ExtractedData
    from ._v1.text_data import TextData
    from ._v1.raw_data import (RawData, TableData, Table, CellData,
                               KeyValueData, ClassData, ContentData)
    from ._v1.config_data import ConfigData
    from ._v1.controller_req_res_data import (ControllerRequestData, ControllerResponseData,
                                              SnapshotData, RecordData, ProcessorFilterData)
else:
    from .document_data import DocumentData
    from .message_data import MessageData
    from .message_item_data import (
        MessageItemData, MessageTypeEnum, MessageCodeEnum)
    from .meta_data import MetaData
    from .page_data import PageData
    from .processor_response_data import ProcessorResponseData
    from .standard_data import StandardData
    from .value_data import ValueData
    from .extracted_data import ExtractedData
    from .text_data import TextData
    from .raw_data import (RawData, TableData, Table, CellData,
                           KeyValueData, ClassData, ContentData)
    from .config_data import ConfigData
    from .controller_req_res_data import (ControllerRequestData, ControllerResponseData,
                                          SnapshotData, RecordData, ProcessorFilterData)
