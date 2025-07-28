# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import time
import glob
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider \
    import TesseractOcrDataServiceProvider as tesseract_parser
from infy_ocr_generator import ocr_generator
from infy_ocr_generator.providers.infy_ocr_engine_data_service_provider \
    import InfyOcrEngineDataServiceProvider
from infy_ocr_generator.providers.tesseract_ocr_data_service_provider \
    import TesseractOcrDataServiceProvider
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider \
    import AzureReadOcrDataServiceProvider as azure_read_parser
from infy_ocr_generator.providers.azure_read_ocr_data_service_provider \
    import AzureReadOcrDataServiceProvider
from infy_dpp_content_extractor.content_extractor.service.image_generator_service import ImageGeneratorService


from infy_dpp_content_extractor.common.app_constant import OcrType
from infy_dpp_content_extractor.common.file_util import FileUtil


class ImagesTextExtractor:
    def __init__(self, text_provider_dict, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

        self.__text_provider_dict = text_provider_dict
        self.__converter_path = self.__text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self.__pytesseract_path = self.__text_provider_dict.get(
            'properties').get('tesseract_path', '')
        self.__ocr_engine_exe_dir_path = self.__text_provider_dict.get(
            'properties').get('ocr_engine_exe_dir_path', '')
        self.__ocr_engine_model_dir_path = self.__text_provider_dict.get(
            'properties').get('ocr_engine_model_dir_path', '')
        self.__ocr_engine_language = self.__text_provider_dict.get(
            'properties').get('ocr_engine_language', '')

    def get_images_text(self, from_files_full_path, out_file_full_path):
        image_path_list = []
        images_json_folder = from_files_full_path + '_files'
        image_json_file_path = glob.glob(
            os.path.join(images_json_folder, '*_image_bbox.json'))
        images_content = FileUtil.load_json(image_json_file_path[0])
        for page in images_content:
            for token in page['tokens']:
                image_path = token['uri'].replace(
                    'file://', out_file_full_path)
                image_path_list.append(image_path)
        ocr_file_list = self.generate_ocr(image_path_list, out_file_full_path)
        image_text_data_list = self.get_text_from_ocr(ocr_file_list)
        index = 0
        for page in images_content:
            for token in page['tokens']:
                token['text'] = image_text_data_list[index]
                index += 1
        FileUtil.save_to_json(image_json_file_path[0], images_content)

        # upload the json file to the work location
        server_file_dir = os.path.dirname(image_json_file_path[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(image_json_file_path[0])
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

    def get_ocr_from_images(self, from_files_full_path, out_file_full_path):
        org_file_path = from_files_full_path
        doc_extension = os.path.splitext(
            org_file_path)[1].lower()
        # pdf to image
        config_data_dict = {
            "format_converter": {
                "pages": [
                ],
                "to_dir": os.path.abspath(out_file_full_path),
                "dpi": 300
            },
            "format_converter_home": self.__converter_path
        }

        image_generator_service_obj = ImageGeneratorService(self.__logger)

        if doc_extension in ['.jpg', '.png', '.jpeg']:
            self.__logger.info('...IMG to JPG conversion started...')
            images_path_list, _ = image_generator_service_obj.convert_img_to_jpg(
                os.path.abspath(org_file_path), config_data_dict)

        if doc_extension in ['.tiff', '.tif']:
            self.__logger.info('...TIFF to JPG conversion started...')
            images_path_list, _ = image_generator_service_obj.convert_tiff_to_jpg(
                os.path.abspath(org_file_path), config_data_dict)

        self.__logger.info('...OCR generation started...')
        ocr_files_path_list = self.generate_ocr(
            images_path_list, out_file_full_path)

        if doc_extension in ['.tiff', '.tif']:
            ocr_path_list = []
            image_path_list = []
            for i, image_path in enumerate(images_path_list):
                image_path = image_path.replace('\\', '/').replace('//', '/').replace(
                    self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
                ocr_path = ocr_files_path_list[i].replace('\\', '/').replace('//', '/').replace(
                    self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

                image_path_list.append(image_path)
                ocr_path_list.append(ocr_path)
            return ocr_path_list, image_path_list

        ocr_file_path = ocr_files_path_list[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        image_file_path = images_path_list[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        return ocr_file_path, image_file_path

    def generate_ocr(self, image_path_list, out_file_full_path):
        '''generate ocr'''
        ocr_path_list = []
        ocr_data_gen_obj, ocr_data_ser_provider = self.__init_data_service_provider_objects(
            self.__text_provider_dict, out_file_full_path)
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '.hocr')
            if len(to_be_ocr_gen_img_list) > 0:
                doc_data_list = [
                    {
                        "doc_path": doc_file_path,
                        "pages": index + 1
                    } for index, doc_file_path in enumerate(to_be_ocr_gen_img_list)
                ]
                ocr_result_list = ocr_data_gen_obj.generate(
                    doc_data_list=doc_data_list)
                ocr_path_list = [ocr_result.get(
                    'output_doc') for ocr_result in ocr_result_list]
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.INFY_OCR_ENGINE):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '.hocr')
            if len(to_be_ocr_gen_img_list) > 0:
                doc_data_list = [
                    {
                        "doc_path": doc_file_path,
                        "pages": index + 1
                    } for index, doc_file_path in enumerate(to_be_ocr_gen_img_list)
                ]
                ocr_result_list = ocr_data_gen_obj.generate(
                    doc_data_list=doc_data_list)
                ocr_path_list = [ocr_result.get(
                    'output_doc') for ocr_result in ocr_result_list]
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '_azure_read.json')
            self.__logger.info(
                f"Already generated azure read ocr files: {generated_ocr_file_list}")
            self.__logger.info(
                f"Azure Read Ocr to be generated for : {to_be_ocr_gen_img_list}")
            if len(to_be_ocr_gen_img_list) > 0:
                doc_data_list = [
                    {
                        "doc_path": doc_file_path,
                        "pages": index + 1
                    } for index, doc_file_path in enumerate(to_be_ocr_gen_img_list)
                ]
                submit_req_result = ocr_data_gen_obj.submit_request(
                    doc_data_list=doc_data_list
                )
                time.sleep(7)
                re_res_result = ocr_data_gen_obj.receive_response(
                    submit_req_result)
                ocr_result_list = ocr_data_gen_obj.generate(
                    api_response_list=re_res_result)
                ocr_path_list = [ocr_result.get('output_doc').replace('\\', '/').replace('//', '/')
                                 for ocr_result in ocr_result_list]

        ocr_path_list.extend(generated_ocr_file_list)
        # upload the ocr files to the work location
        server_file_dir = os.path.dirname(ocr_path_list[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(ocr_path_list[0])
        self._upload_data(f'{local_dir}', f'{server_file_dir}')
        return ocr_path_list

    def _check_existing_ocr_files(self, image_path_list, ocr_file_name):
        azure_read_ocr_file_tup_list = [(f'{x}{ocr_file_name}', os.path.exists(
            f'{x}{ocr_file_name}')) for x in image_path_list]
        to_be_ocr_gen_img_list = [x[0].replace(ocr_file_name, '').replace(
            '\\', '/').replace('//', '/')
            for x in azure_read_ocr_file_tup_list if not x[1]]
        generated_ocr_file_list = [x[0].replace('\\', '/').replace('//', '/')
                                   for x in azure_read_ocr_file_tup_list if x[1]]
        return to_be_ocr_gen_img_list, generated_ocr_file_list

    def get_text_from_ocr(self, ocr_file_list):
        '''get content from bbox using ocr parser'''
        image_text_data_list = []
        token_type_value = 3
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            ocr_parser_data_service_provider = tesseract_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.INFY_OCR_ENGINE):
            ocr_parser_data_service_provider = tesseract_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            ocr_parser_data_service_provider = azure_read_parser()

        for ocr_file in ocr_file_list:
            ocr_obj = ocr_parser.OcrParser([ocr_file],
                                           data_service_provider=ocr_parser_data_service_provider,
                                           config_params_dict={
                'match_method': 'regex', 'similarity_score': 1})

            lines_dict_list = ocr_obj.get_tokens_from_ocr(
                token_type_value=token_type_value)
            if lines_dict_list:
                content_text = ""
                for token in lines_dict_list:
                    content_text += token["text"] + " "
                image_text_data_list.append(content_text)
            else:
                image_text_data_list.append('')

        return image_text_data_list

    def __init_data_service_provider_objects(self, provider_settings, out_file_full_path):
        def _format_azure_config_param(config_params_dict, provider_key):
            # temp_dict = config_params_dict[f"azure_{provider_key}"]
            temp_dict = config_params_dict.get("properties")
            # if provider_settings.get("provider_name").startswith(f"azure_{provider_key}")
            new_dict = {}
            new_dict['computer_vision'] = {
                'subscription_key': temp_dict.get('subscription_key'),
                f'api_{provider_key}': temp_dict
            }
            return {"azure": new_dict}

        ocr_gen_obj = None
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            data_service_provider = TesseractOcrDataServiceProvider(
                config_params_dict={'tesseract': {
                    'pytesseract_path': self.__pytesseract_path}},
                logger=self.__logger,
                output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.INFY_OCR_ENGINE):
            data_service_provider = InfyOcrEngineDataServiceProvider(
                config_params_dict={
                    'ocr_engine': {
                        'exe_dir_path': self.__ocr_engine_exe_dir_path,
                        'model_dir_path': self.__ocr_engine_model_dir_path,
                        'lang': self.__ocr_engine_language,
                        'ocr_format': 'hocr',  # Only hocr is required
                    }},
                logger=self.__logger,
                output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            data_service_provider = AzureReadOcrDataServiceProvider(
                config_params_dict=_format_azure_config_param(
                    provider_settings, 'read'), logger=self.__logger,
                output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )

        return ocr_gen_obj, data_service_provider

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e
