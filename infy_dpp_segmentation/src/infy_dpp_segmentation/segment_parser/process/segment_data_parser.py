# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk
from infy_dpp_sdk.data import *

from infy_dpp_segmentation.segment_parser.process.segment_data import SegementData

PROCESSEOR_CONTEXT_DATA_NAME = "segment_data_parser"


class SegmentDataParser(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self._processor_response_data = ProcessorResponseData()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        context_data = context_data if context_data else {}
        segment_processor_config = config_data['SegmentDataParser']
        processor_data = {
            "document_data": document_data.json(), "context_data": context_data}
        raw_data_dict = document_data.raw_data.dict()
        segment_data_list = raw_data_dict.get('segment_data')
        pattern = None
        layout = None
        for layout_key, val in segment_processor_config.get('layout').items():
            if val.get('enabled'):
                layout = layout_key
        for pattern_key, val in segment_processor_config.get('pattern').items():
            if val.get('enabled'):
                pattern = pattern_key

        updated_segment_data_list = SegementData().update_sequence(
            segment_data_list, layout, pattern)
        document_data.raw_data.segment_data = updated_segment_data_list
        # raw_data=infy_dpp_sdk.data.RawData(table_data=[],key_value_data=[],heading_data=[],
        #                                         page_header_data=[],
        #                                         page_footer_data=[],other_data=[],segment_data=updated_segment_data_list)
        # document_data.raw_data = raw_data

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'parsed_segment_data': updated_segment_data_list}

        # Populate response data
        self._processor_response_data.document_data = document_data
        self._processor_response_data.context_data = context_data

        return self._processor_response_data
