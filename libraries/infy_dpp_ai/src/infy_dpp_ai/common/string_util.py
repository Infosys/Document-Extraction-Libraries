# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json

class StringUtil():
    """Util class for parsing string into a json object"""

    @staticmethod
    def parse_string_to_json(input_data: str):
        """Parse string to json"""
        try:
            return json.loads(input_data)
        except json.JSONDecodeError:
            if input_data.strip().startswith("```json") and input_data.strip().endswith("```"):
                code_content = input_data.strip()[7:-3].strip()
                try:
                    return json.loads(code_content)
                except json.JSONDecodeError:
                    pass
        return input_data