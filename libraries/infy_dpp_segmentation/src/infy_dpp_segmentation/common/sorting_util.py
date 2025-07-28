# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Image Sort Util class"""

import re
import os


class ImageSortUtil():
    """Util class for sorting image files"""

    @staticmethod
    def atoi(text):
        return int(text) if text.isdigit() else text

    @staticmethod
    def natural_keys(text):
        basename = os.path.basename(text)
        match = re.match(r'^(\d+)', basename)
        if match:
            return (int(match.group(1)), basename)
        else:
            return (float('inf'), basename)

    @classmethod
    def sort_image_files(cls, img_file_path_list):
        return sorted(img_file_path_list, key=cls.natural_keys)
