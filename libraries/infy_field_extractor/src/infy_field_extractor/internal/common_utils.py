# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import datetime
import os
import shutil
from datetime import datetime


class CommonUtils:
    """Common util class"""

    @staticmethod
    def make_dir_with_timestamp(folderpath, img_name):
        timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
        folderpath = os.path.join(
            folderpath, img_name+'_'+timestr)
        os.mkdir(folderpath)
        return folderpath

    @staticmethod
    def delete_dir_recursively(folderpath):
        shutil.rmtree(folderpath)

    @staticmethod
    def archive_file(original_file_path):
        if os.path.exists(original_file_path):
            ext = os.path.splitext(original_file_path)[1]
            suffix = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ext
            new_name = f'{original_file_path.replace(ext,"")}_{suffix}'
            os.rename(original_file_path, new_name)
