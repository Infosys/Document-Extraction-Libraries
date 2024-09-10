# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from infy_ocr_generator import ocr_generator
from infy_ocr_generator.providers.apache_pdfbox_data_service_provider \
    import ApachePdfboxDataServiceProvider
# from infy_dpp_content_extractor.content_extractor.service.image_generator_service import ImageGeneratorService
# from infy_dpp_content_extractor.content_extractor.service import ImagesFromPdfExtractorService
from infy_dpp_content_extractor.common.file_util import FileUtil


class PdfBoxBasedOcrGenerator:
    def __init__(self, text_provider_dict):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self.__converter_path = text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self._org_pdf_file_path = None

    # def generate_ocr_json_for_pdf(self, from_files_full_path="", out_file_full_path="", ocr_data_gen_obj=None):
    def generate_ocr_json_for_pdf(self, from_files_full_path="", out_file_full_path=""):
        '''generate ocr json file for pdf as input.'''
        # is_upload = False
        doc_data_list = [
            {
                "doc_path": os.path.abspath(from_files_full_path)
            }
        ]
        # if not ocr_data_gen_obj:
        #     is_upload = True
        #     ocr_data_gen_obj, _ = self.__init_data_service_provider_objects(
        #         out_file_full_path)
        ocr_data_gen_obj, _ = self.__init_data_service_provider_objects(
            out_file_full_path)
        ocr_result_list = ocr_data_gen_obj.generate(
            doc_data_list=doc_data_list)
        raw_ocr_file_path = [ocr_result.get(
            'output_doc') for ocr_result in ocr_result_list][0]

        # if is_upload:
        # upload the pdf ocr json file to the work location
        server_file = raw_ocr_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        # local_dir = os.path.dirname(out_file_full_path)
        self.__file_sys_handler.put_file(raw_ocr_file_path, server_file)
        # self._upload_data(f'{local_dir}', f'{server_file_dir}')
        raw_ocr_file_path = server_file
        return raw_ocr_file_path

    def generate_ocr(self, image_path_list, from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path):
        '''generate ocr for the given image path list'''
        self._org_pdf_file_path = from_files_full_path
        ocr_path_list = []
        ocr_data_gen_obj, ocr_data_ser_provider = self.__init_data_service_provider_objects(
            out_file_full_path)

        to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
            image_path_list, '_pdfbox.json')
        # modifiy to make abs path using Storage path
        # raw_ocr_file_path = self.__file_sys_handler.get_abs_path(
        #     pdf_apache_pdfbox_ocr_file_path)
        # download to local path from storage path
        raw_ocr_file_path = out_file_full_path+"/" + \
            os.path.basename(pdf_apache_pdfbox_ocr_file_path)
        self.__file_sys_handler.get_file(
            pdf_apache_pdfbox_ocr_file_path, raw_ocr_file_path)
        # raw_ocr_file_path1 = self.__file_sys_handler.get_abs_path(
        #     pdf_apache_pdfbox_ocr_file_path)
        # raw_ocr_file_path = self.__file_sys_handler.get_storage_root_uri()+"/" + \
        #     pdf_apache_pdfbox_ocr_file_path
        # raw_ocr_file_path = self.generate_ocr_json_for_pdf(from_files_full_path=from_files_full_path,
        #                                                    out_file_full_path=out_file_full_path,
        #                                                    ocr_data_gen_obj=ocr_data_gen_obj)
        # doc_data_list = [
        #     {
        #         "doc_path": os.path.abspath(self._org_pdf_file_path)
        #     }
        # ]
        # # generate ocr json file for pdf as input.
        # ocr_result_list = ocr_data_gen_obj.generate(
        #     doc_data_list=doc_data_list)
        # raw_ocr_file_path = [ocr_result.get(
        #     'output_doc') for ocr_result in ocr_result_list][0]
        if len(to_be_ocr_gen_img_list) > 0:
            rescale_data_list = [{
                'doc_page_num': os.path.basename(x).split('.', 1)[0],
                'doc_page_width': 0,
                'doc_page_height': 0,
                # os.path.abspath(x),
                'doc_file_path': out_file_full_path+'/'+os.path.basename(x),
                'doc_file_extension': 'jpg'
            } for x in to_be_ocr_gen_img_list]
            page_ocr_list = ocr_data_ser_provider.rescale_dimension(
                raw_ocr_file_path, rescale_data_list)
            ocr_path_list = [ocr_result.get('output_doc').replace('\\', '/').replace('//', '/')
                             for ocr_result in page_ocr_list]
        ocr_path_list.extend(generated_ocr_file_list)

        # upload the ocr files to the work location
        server_file_dir = os.path.dirname(ocr_path_list[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(ocr_path_list[0])
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        ocr_files_path_list = []
        for ocr_file_path in ocr_path_list:
            images_file_path = ocr_file_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
            ocr_files_path_list.append(images_file_path)

        # FileUtil.empty_dir(local_dir)
        return ocr_files_path_list

    def _upload_data(self, local_file_path, server_file_path):
        try:
            # TODO: uploading is not working in local
            # self.__file_sys_handler.put_folder(
            #     local_file_path, os.path.dirname(server_file_path))
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

    def _check_existing_ocr_files(self, image_path_list, ocr_file_name):
        azure_read_ocr_file_tup_list = [(f'{x}{ocr_file_name}', os.path.exists(
            f'{x}{ocr_file_name}')) for x in image_path_list]
        to_be_ocr_gen_img_list = [x[0].replace(ocr_file_name, '').replace(
            '\\', '/').replace('//', '/')
            for x in azure_read_ocr_file_tup_list if not x[1]]
        generated_ocr_file_list = [x[0].replace('\\', '/').replace('//', '/')
                                   for x in azure_read_ocr_file_tup_list if x[1]]
        return to_be_ocr_gen_img_list, generated_ocr_file_list

    def __init_data_service_provider_objects(self, out_file_full_path):
        ocr_gen_obj = None
        data_service_provider = ApachePdfboxDataServiceProvider(
            config_params_dict={
                "format_converter": {
                    "format_converter_path": self.__converter_path
                }
            }, logger=self.__logger, output_dir=out_file_full_path)
        ocr_gen_obj = ocr_generator.OcrGenerator(
            data_service_provider=data_service_provider
        )
        return ocr_gen_obj, data_service_provider

    # def get_images_path_list(self, from_files_full_path, out_file_full_path) -> list:
    #     '''getting images of pdf file page by page'''
    #     self._org_pdf_file_path = from_files_full_path
    #     # pdf to image
    #     config_data_dict = {
    #         "format_converter": {
    #             "pages": [
    #             ],
    #             "to_dir": os.path.abspath(out_file_full_path),
    #             "dpi": 300
    #         },
    #         "format_converter_home": self.__converter_path
    #     }
    #     self.__logger.info('...PDF to JPG conversion started...')
    #     image_generator_service_obj = ImageGeneratorService()
    #     images_path_list, _ = image_generator_service_obj.convert_pdf_to_image(
    #         os.path.abspath(self._org_pdf_file_path), config_data_dict)

    #     # upload the json file to the work location
    #     server_file_dir = os.path.dirname(images_path_list.replace('\\', '/').replace('//', '/').replace(
    #         self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
    #     local_dir = os.path.dirname(images_path_list)
    #     self.__upload_data(f'{local_dir}', f'{server_file_dir}')

    #     images_content_path_file_path = images_path_list.replace('\\', '/').replace('//', '/').replace(
    #         self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

    #     return images_content_path_file_path

    # def __upload_data(self, local_file_path, server_file_path):
    #     try:
    #         self.__file_sys_handler.put_folder(
    #             local_file_path, server_file_path)
    #         self.__logger.info(
    #             f'Folder {local_file_path} uploaded successfully')
    #     except Exception as e:
    #         self.__logger.error(
    #             f'Error while uploading data to {server_file_path} : {e}')
    #         raise e
