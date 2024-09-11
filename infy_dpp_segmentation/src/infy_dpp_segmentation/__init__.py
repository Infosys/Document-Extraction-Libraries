# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from . import (common, segment_generator, segment_classifier, page_column_detector,
               segment_sequencer, segment_merger, segment_consolidator, chunk_generator)


# Validate module installed
from .common.dependency_util import DependencyUtil
VALIDATE_MODULE_INSTALLED = ['infy_dpp_sdk',
                             'infy_common_utils',
                             'infy_ocr_generator',
                             'infy_ocr_parser']
for x in VALIDATE_MODULE_INSTALLED:
    DependencyUtil.is_module_installed(x)
