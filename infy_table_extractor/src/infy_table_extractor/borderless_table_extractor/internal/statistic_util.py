# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class StatisticUtil:
    """Class to find statistics"""
    @classmethod
    def get_confidence_score(cls, hocr_line_prediction, img_line_prediction):
        """Get confidence score"""
        row_pos_len_list = [len(img_line_prediction['rows']),
                            len(hocr_line_prediction['rows'])]
        col_pos_len_list = [len(img_line_prediction['cols']),
                            len(hocr_line_prediction['cols'])]
        row_score = round(min(row_pos_len_list)/max(row_pos_len_list), 2)
        col_score = round(min(col_pos_len_list)/max(col_pos_len_list), 2)
        return row_score, col_score
