# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import requests
import base64

class ResourceSaver:
    def __init__(self, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def save_resource_local(self, doc_file_path, resource_base_path, new_filename):
        self.__file_sys_handler.create_folders(resource_base_path)
        resources_file_path = f"{resource_base_path}/{new_filename}"
        self.__file_sys_handler.copy_file(doc_file_path, resources_file_path)
        resource_file_dict = {
            'type': 'doc_file_path',
            'path': resources_file_path
        }
        return resource_file_dict

    def save_resource_server(self, doc_file_path, new_filename, resource_base_path):
        resource_file_path =self.__file_sys_handler.get_abs_path(doc_file_path).replace('filefile://','')
        
        upload_url = f"{resource_base_path}/api/v1/resource/upload_file"
        with open(resource_file_path, "rb") as file:
            files = {'file': (new_filename, file, 'application/pdf')}
            response = requests.post(upload_url, files=files)

        if response.status_code == 200 or response.status_code == 204:
            self.__logger.info('File uploaded successfully.')
        else:
            self.__logger.info(f'Failed to upload the file. Status code: {response.status_code}')
            self.__logger.info(response.text)
           
        resource_file_dict = {
            'type': 'url_file_path',
            'path': new_filename
        }
        return resource_file_dict
