# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for PydanticUtil class"""

import pydantic


class PydanticUtil():
    """Util class for handling pydantic version specific methods"""

    @classmethod
    def get_json_str(cls, obj: any, indent=0) -> str:
        """
        Get json string from pydantic object.

        Args:
            obj (any): Pydantic object.
            indent (int, optional): Indentation level for the JSON string. Defaults to 0.

        Returns:
            str: JSON string representation of the pydantic object.
        """
        if pydantic.VERSION.startswith('1.'):
            data_json = obj.json(indent=indent)
        else:
            data_json = obj.model_dump_json(indent=4)
        return data_json
