# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import tiktoken


class TokenizerService():

    SECTION_TOKENIZER = "TOKENIZER"
    ENCODING_P50K_BASE = "p50k_base"

    def __init__(self,tiktoken_cache_dir):
        os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

    def count_tokens(self, text, encoding_name):
        encoding = tiktoken.get_encoding(encoding_name)
        count = len(encoding.encode(text))
        return count
