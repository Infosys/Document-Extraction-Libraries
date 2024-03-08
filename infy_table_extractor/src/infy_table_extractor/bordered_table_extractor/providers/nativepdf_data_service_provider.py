# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from infy_common_utils.format_converter import ConvertAction
import infy_common_utils.format_converter as format_converter
from infy_table_extractor.bordered_table_extractor.interface.data_service_provider_interface import DataServiceProviderInterface
format_converter.format_converter_jar_home = os.environ['FORMAT_CONVERTER_HOME']


class NativePdfDataServiceProvider(DataServiceProviderInterface):
    """Native pdf Data Service Provider"""

    def __init__(self, logger=None, log_level=None):
        """Creates an instance of Native pdf Data Service Provider

        Args:
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        """
        super(NativePdfDataServiceProvider, self).__init__(logger, log_level)
        self.logger.info("Initialized successfully")

    def get_tokens(self, token_type_value, img=None, file_data_list=None):
        """Method to be implemented to get all tokens (word, phrase or line) and its 
            bounding box as x, y, width and height from an image as a list of dictionary.
            Currently word token is only required.

        Args:
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            img (np.array): Read image as np array of the original image.
            file_data_list (FILE_DATA, optional): List of all file datas. Each file data has
                the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file based 
                on the image dimensions or type of file extension.
                Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented
        """
        raise NotImplementedError

    def get_text(self, img, img_cell_bbox_list,
                 file_data_list=None, additional_info=None, temp_folderpath=None):
        """Method to be implemented to return the text from the list of
        cell images or bbox of the original image as a list of dictionary.
        (Eg. [{'cell_id': str,'cell_text':'{{extracted_text}}', 'cell_bbox':[x, y, w, h]}]

        Args:
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            img (np.array): Read image as np array of the original image.
            file_data_list (FILE_DATA, optional): List of all file datas. Each file data has
                the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file based 
                on the image dimensions or type of file extension.
                Defaults to None.

        Returns:
            [GET_TEXT_OUTPUT]: list of dict containing text and its bbox.
        """
        pdf_data = self._get_pdf_data(file_data_list)
        cell_bbox_list = [cell['cell_bbox'] for cell in img_cell_bbox_list]
        config_param_dict = {
            "pages": [pdf_data['pages'][0]],
            "bboxes": cell_bbox_list,
            "page_dimension": {"width": img.shape[1], "height": img.shape[0]}}
        convert_action = ConvertAction.PDF_TO_JSON
        output = format_converter.FormatConverter.execute(
            pdf_data['path'], convert_action, config_param_dict)
        result = [{'cell_text': d['text'], 'cell_bbox':d['bbox']}
                  for d in output[0][0]['regions']]
        return result

    def _get_pdf_data(self, file_data_list):
        for file_data in file_data_list:
            if file_data['path'].lower().endswith('pdf'):
                return file_data
        raise Exception("Pdf file not found")
