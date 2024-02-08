# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import base64
import json
import subprocess
import zlib
from .infy_json_encoder import InfyJSONEncoder


class ExtractionUtil:
    @classmethod
    def run_command(cls, run_command):
        sub_process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True, shell=True)
        stdout, stderr = sub_process.communicate()
        return stdout.strip().split('\n')[-1], stderr

    @classmethod
    def convert_data_model_to_json(cls, data):
        return json.dumps(InfyJSONEncoder().encode(data))

    @classmethod
    def convert_dict_to_base64_str(cls, data_dict):
        json_str = cls.convert_data_model_to_json(data_dict)
        return base64.b64encode(json_str.encode("utf-8")).decode()

    @classmethod
    def compress_data(cls, data):
        json_str = cls.convert_data_model_to_json(data)
        return base64.b64encode(zlib.compress(json_str.encode())).decode()

    @classmethod
    def decode_data(cls, data):
        def _decode(encoded_str):
            try:
                decoded = json.loads(json.loads(
                    base64.b64decode(encoded_str).decode("utf-8")))
                return decoded
            except Exception:
                return encoded_str
        return _decode(data)
