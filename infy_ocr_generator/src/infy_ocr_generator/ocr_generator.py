# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#


from infy_ocr_generator.interface.data_service_provider_interface import (
    SUB_RE_API_STRUCTURE, DataServiceProviderInterface, DOC_DATA)


class OcrGenerator():
    """Class providing APIs to generate OCR file using a specified OCR tool"""

    def __init__(self, data_service_provider: DataServiceProviderInterface):
        """Creates an instance of OCR generator.

        Args:
            data_service_provider (DataServiceProviderInterface):Provider to generate OCR file using a specified OCR tool.

        Raises:
            Exception: Valid `data_service_provider` is required.
        """
        if data_service_provider:
            self.data_service_provider = data_service_provider
        else:
            raise Exception("Valid `data_service_provider` is required.")

    def set_data_service_provider(self, data_service_provider: DataServiceProviderInterface):
        """Setter method to switch `data_service_provider` at runtime.

        Args:
            data_service_provider (DataServiceProviderInterface): Provider object
        """
        self.data_service_provider = data_service_provider

    def submit_request(self, doc_data_list: [DOC_DATA]) -> [SUB_RE_API_STRUCTURE]:
        """API to submit request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents and its pages. e.g, ['doc_path':'c:/1.jpg','pages':'1']

        Raises:
            Exception: Please provide valid doc_data_list(pages) param

        Returns:
            [SUB_RE_API_STRUCTURE]: List of dictionary
        """
        if not self.__is_valid_input_pages(doc_data_list):
            raise Exception(
                "Please provide valid doc_data_list(pages) param")
        return self.data_service_provider.submit_request(doc_data_list)

    def receive_response(self, submit_req_result: [SUB_RE_API_STRUCTURE],
                         rerun_unsucceeded_mode: bool = False) -> [SUB_RE_API_STRUCTURE]:
        """API to Received response of asynchorouns call submit request.

        Args:
            submit_req_result ([SUB_RE_API_STRUCTURE]): Response structure of `submit_request` api
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call. Defaults to False.

        Returns:
            [SUB_RE_API_STRUCTURE]: List of dictionary
        """
        result_list = self.data_service_provider.receive_response(
            submit_req_result, rerun_unsucceeded_mode)
        return result_list

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) -> list:
        """API to generate OCR based on given OCR provider.

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file.Defaults to None.

        Raises:
            Exception: Please provide valid pages in doc_data_list param

        Returns:
            list: List of generated ocr file path.
        """
        if doc_data_list and (not self.__is_valid_input_pages(doc_data_list)):
            raise Exception(
                "Please provide valid pages in doc_data_list param")
        return self.data_service_provider.generate(doc_data_list, api_response_list)

    @classmethod
    def __is_valid_input_pages(cls, doc_data_list: list):
        """internal page number validator"""

        is_valid = True
        try:
            _ = [int(doc_data['pages'])
                 for doc_data in doc_data_list if not doc_data['doc_path'].lower().endswith('.pdf')]
        except Exception:
            is_valid = False
        return is_valid
