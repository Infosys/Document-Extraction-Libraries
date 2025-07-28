# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import imageio
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider import AzureReadOcrDataServiceProvider
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
from infy_dpp_attribute_extractor.common.file_util import FileUtil
from infy_dpp_attribute_extractor.rd_based_attribute_extractor.service import FieldExtractorService

PROCESSEOR_CONTEXT_DATA_NAME = "rd_based_attribute_extractor"


class RdBasedAttributeExtractor(infy_dpp_sdk.interface.IProcessor):

    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        def response_data(get_bbox_for_result, region_definition_array):
            response_data = {}
            output_list = []
            error = get_bbox_for_result['error']
            warning = get_bbox_for_result['warnings']
            regions = get_bbox_for_result["regions"]

            # id = to_do logic
            name = regions[0]['anchorTextBBox'][0]['anchorText'][0][0]
            message = {
                'error': error,
                'warning': warning
            }
            values = []

            if error:
                self.__logger.error(
                    f'Error in getting BBox: {error}')

            if regions:
                for region in regions:
                    output = region["regionBBox"][0]
                    output_list.append(output)
                    text_obj = {
                        "id": "to_do",
                        "text": output['text'][0],
                        "confidencePct": output['confidencePct'],
                        "bbox": output['bbox'],
                        "page": output['page']
                    }
                    extraction_technique = {
                        "default": {
                            "confidencePct": output['confidencePct'],
                            "selected": True
                        }
                    }

                    value = {
                        "message": message,
                        "type": "text_obj_list",
                        "text_obj_list": text_obj,
                        "extractionTechnique": extraction_technique
                    }
                    values.append(value)

                debug_info = []
                info = {
                    "ocr_parser": {
                        "input": region_definition_array,
                        "output": output_list
                    },
                    "field_extractor": []
                }
                debug_info.append(info)
                additional_info = {
                    "rd_found": name,
                    "rd_not_found": [],
                    "debug_info": debug_info
                }

                response_data = {
                    "id": "to_do",
                    "name": name,
                    "message": message,
                    "values": values,
                    "additional_info": additional_info
                }
            return response_data

        self.__logger.debug('Rd Based Attribute Extraction Started')
        processor_response_data = ProcessorResponseData()
        rd_based_attribute_extractor_config_data = config_data.get(
            'RdBasedAttributeExtractor', {})
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        out_file_full_path = f'{from_files_full_path}_files'
        if not os.path.exists(out_file_full_path):
            os.makedirs(out_file_full_path)

        raw_attributes = []
        content_extracted = context_data.get('content_extractor')
        if content_extracted:
            ocr_file_path = content_extracted.get(
                'content_extractor_image').get('image_ocr').get('image_ocr_file_path')

            if ocr_file_path:
                image_file_path = content_extracted.get(
                    'content_extractor_image').get('image_ocr').get('image_file_path')

                for ocr_tool in rd_based_attribute_extractor_config_data.get(
                        'ocr_tool_provider', {}):
                    if not ocr_tool.get('enabled'):
                        continue
                    else:
                        ocr_file_list = []
                        if ocr_tool.get('name') == 'tesseract_ocr':
                            ocr_service_provider = TesseractOcrDataServiceProvider()
                        elif ocr_tool.get('name') == 'azure_read_ocr':
                            ocr_service_provider = AzureReadOcrDataServiceProvider()
                        else:
                            self.__logger.error(
                                f'Invalid OCR Tool Provider: {ocr_tool.get("name")}')

                        ocr_file = self.__file_sys_handler.get_bucket_name() + ocr_file_path
                        ocr_file_list.append(ocr_file)
                        ocr_obj = ocr_parser.OcrParser(
                            ocr_file_list, data_service_provider=ocr_service_provider)

                        attributes = rd_based_attribute_extractor_config_data.get(
                            'attributes')

                        for attribute in attributes:
                            if not attribute.get('attributeDefinitions').get('enabled'):
                                continue
                            else:
                                rd = attribute.get('attributeDefinitions').get(
                                    'valueRegionDefinition')

                                region_definition = json.dumps(rd, indent=4)
                                region_definition_array = json.loads(
                                    region_definition)

                                image_file_full_path = self.__file_sys_handler.get_bucket_name() + \
                                    image_file_path
                                img = imageio.imread(image_file_full_path)
                                scaling_factor = ocr_obj.calculate_scaling_factor(
                                    img.shape[1], img.shape[0])['scalingFactor']

                                get_bbox_for_result = ocr_obj.get_bbox_for(
                                    region_definition_array, scaling_factor=scaling_factor)

                                raw_attributes.append(response_data(
                                    get_bbox_for_result, region_definition_array))

                                label = attribute.get(
                                    'attributeDefinitions').get('label')
                                values = raw_attributes[-1].get('values')

                                for value in values:
                                    bbox = value.get(
                                        'text_obj_list').get('bbox')
                                    page = value.get(
                                        'text_obj_list').get('page')

                                    field_extractor_service_obj = FieldExtractorService(
                                        out_file_full_path)
                                    field_extractor_output = field_extractor_service_obj.call_text_extractor(
                                        image_file_full_path, label, bbox, ocr_obj, scaling_factor, page)

                                    field_extractor = raw_attributes[-1].get('additional_info').get('debug_info')[
                                        0].get('field_extractor')
                                    field_extractor.append(
                                        field_extractor_output)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'raw_attributes': raw_attributes
        }
        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        self.__logger.debug('Rd Based Attribute Extraction Completed')
        return processor_response_data
