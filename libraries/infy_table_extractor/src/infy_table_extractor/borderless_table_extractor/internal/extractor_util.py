# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import copy
import datetime

import numpy as np
import pandas as pd
import json
import re


class ExtractorUtil:
    """Utill class for all bbox related activities."""
    @classmethod
    def convert_to_other(cls, phrase_token_data, line_pos, output_file, predicted_line_pos,
                         conf_score_list, config_param_dict):
        """Converts the lines to html and json"""

        # '#WL125' :multiline : new table change starts...
        def _reshuffle_matrix(t_matrix):
            try:
                num_tabl = np.array(t_matrix)
                new_table = []
                start = 0
                end = -1
                df = pd.DataFrame(num_tabl)
                for rows in range(0, df.shape[0]):
                    if num_tabl[rows, 2] == '':
                        end = rows
                    else:
                        start = rows
                    new_table.append([start, end])
                # getting the row range
                f_end = []
                f_start = []
                row_range_list = []
                for i in range(len(new_table)-1):
                    if(new_table[i+1][0] > new_table[i][0]):
                        f_end = new_table[i][1]
                        f_start = new_table[i][0]
                        row_range_list.append([f_start, f_end])
                # appending last value
                row_range_list.append(new_table[-1])

                # concatenating the empty rows...
                fin_table = [
                    ["" for x in range(df.shape[1])] for y in range(len(row_range_list))]
                for j in range((df.shape[1])-1):
                    for i in range(len(row_range_list)):
                        s = row_range_list[i][0]
                        l = row_range_list[i][1]
                        for k in range(l-s+1):
                            if (t_matrix[s:l+1][k][j]) == '':
                                fin_table[i][j] += (t_matrix[s:l+1][k][j])
                            else:
                                fin_table[i][j] += (t_matrix[s:l+1]
                                                    [k][j])+"<br>"
                return fin_table
            except Exception as e:
                print(e)
        # '#WL125' ends...

        line_pos_cp = copy.deepcopy(line_pos)
        table_matrix = [["" for x in range(len(line_pos_cp['cols']))]
                        for y in range(len(line_pos_cp['rows']))]

        for token_data in phrase_token_data:
            l, t, r, h, = token_data['bbox']
            word = token_data['text']
            prev_row = -1
            for i, row in enumerate(line_pos_cp['rows']):
                is_col_found = False
                if t >= prev_row and h//1 <= row:
                    prev_col = -1
                    for j, col in enumerate(line_pos_cp['cols']):
                        if l >= prev_col and l <= col:
                            table_matrix[i][j] += " " + \
                                word if table_matrix[i][j] else word
                            is_col_found = True
                            break
                        prev_col = col
                    prev_row = row
                if is_col_found:
                    break
        # TODO Below logic causing issue to existing code.
        # Hence commenting it and this logic should be revisited by RASHMI
        # WL125: calling new table
        # new_table_form = _reshuffle_matrix(table_matrix)
        # html_data, json_data, tab_shape = _convert_matrix(
        #     new_table_form)  # passing new table

        df, html_data, json_data, tab_shape = cls.convert_matrix(
            table_matrix, config_param_dict)
        custom_table = ExtractorUtil.extract_custom_cells(
            df, config_param_dict)
        json_data = custom_table if custom_table else json_data
        hocr_predicted_line_pos = predicted_line_pos[0]
        img_predicted_line_pos = predicted_line_pos[1]
        if output_file:
            with open(output_file, 'w') as file_out:
                validation_html = f"""<table>
                    <tr><td></td><td>Expected</td><td>Actual</td></tr>
                    <tr><td>Row</td><td>{len(hocr_predicted_line_pos['rows'])}</td><td>{tab_shape[0]}</td></tr>
                    <tr><td>Column</td><td>{len(hocr_predicted_line_pos['cols'])}</td><td>{tab_shape[1]}</td></tr>
                    </table>"""
                # TODO(Raj) : Remove this conf score populating in html file after development
                score_html = f"""<table>
                    <tr><td></td><td>From Ocr</td><td>From Image</td><td>Conf Score</td></tr>
                    <tr><td>Row</td><td>{len(hocr_predicted_line_pos['rows'])}</td><td>{len(img_predicted_line_pos['rows'])}</td><td>{conf_score_list[0]}</td></tr>
                    <tr><td>Column</td><td>{len(hocr_predicted_line_pos['cols'])}</td><td>{len(img_predicted_line_pos['cols'])}</td><td>{conf_score_list[1]}</td></tr>
                    </table>"""
                file_out.write(f"""<table><tr><td>Validation</td><td colspan="2">&nbsp;</td><td>Score</td>
                            <tr><td>{validation_html}</td><td colspan="2">&nbsp;</td><td>{score_html}</td></tr>
                            </table>"""
                               )
                file_out.write(html_data)
        return json_data

    @classmethod
    def merge_img_hocr_position(cls, img_predicted_line_pos, hocr_predicted_line_pos):
        """Merger hocr module and image module predicted lines """
        img_pred_col_pos = copy.deepcopy(img_predicted_line_pos['cols'])
        ocr_pred_col_pos = copy.deepcopy(hocr_predicted_line_pos['cols'])
        for col_pos in img_pred_col_pos:
            new_pos_idx, new_pos = [], []
            for idx, phrase_col in enumerate(ocr_pred_col_pos):
                phrase_col = phrase_col['bbox']
                # phrase col right <= line col
                if phrase_col[2] <= col_pos:
                    new_pos_idx.append(idx)
                    new_pos.append(phrase_col)
            if len(new_pos) > 1:
                for idx in range(len(new_pos)):
                    if idx+1 == len(new_pos):
                        break
                    # get and add new mid pos from two phrase
                    img_pred_col_pos.append(
                        new_pos[idx+1][0] - ((new_pos[idx+1][0]-new_pos[idx][2])//2))
            # pop item once it matched
            try:
                _ = [ocr_pred_col_pos.pop(pop_id) for pop_id in new_pos_idx]
            except:
                pass
        img_pred_col_pos.sort()
        img_predicted_line_pos['cols'] = img_pred_col_pos
        return {'rows': img_predicted_line_pos['rows'], 'cols': img_predicted_line_pos['cols']}

    @classmethod
    def get_phrases_from_words(cls, tokens):
        """Returns phrase from given token"""
        tokens = sorted(
            tokens, key=lambda b: b.get("bbox")[1]+b.get("bbox")[0], reverse=False)
        phrases_dict_list = []
        words_done = []
        try:
            for t in tokens:
                text = t.get("text")
                t_x, t_y, t_r, t_b = t.get("bbox")
                t_w, t_h = t_r-t_x, t_b-t_y
                word_space = 1.5 * t_h
                if t not in words_done:
                    words_done.append(t)
                    x, y, h = t_x, t_y, t_h
                    for b in tokens:
                        b_x, b_y, b_r, b_b = b.get("bbox")
                        b_w, b_h = b_r-b_x, b_b-b_y
                        is_cur_word_left_within_space = (
                            (t_x+t_w) < b_x <= (t_x+t_w+word_space))
                        is_cur_word_bottom_within_line = (
                            t_y <= b_y+b_h/2 <= (t_y+t_h))
                        is_not_done = (b not in words_done)
                        if(is_cur_word_bottom_within_line and is_cur_word_left_within_space and is_not_done):
                            text += " "+b.get("text")
                            t_x, t_y, t_w, t_h = b_x, b_y, b_w, b_h
                            if t_y < y:
                                y = t_y
                            if h < t_h:
                                h = t_h
                            words_done.append(b)
                    w, h = (t_x+t_w-x), t_h
                    phrases_dict_list.append(
                        {"text": text, "bbox": [x, y, x+w, y+h]})
        except:
            pass
        return phrases_dict_list

    @classmethod
    def create_temp_dir(cls, debug_mode_check, folderpath, img_name):
        """Creates temp directory"""
        try:
            timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            folderpath = os.path.join(
                os.path.abspath(folderpath), img_name if debug_mode_check else img_name+'_'+timestr)
            os.mkdir(folderpath)
        except:
            pass
        return folderpath

    @classmethod
    def get_updated_config_dict(cls, from_dict, default_dict):
        """Method to update the default"""
        config_dict_temp = copy.deepcopy(default_dict)
        if from_dict is None:
            return config_dict_temp
        for key in from_dict:
            config_dict_temp[key] = from_dict[key]
        return config_dict_temp

    @classmethod
    def convert_matrix(cls, table_matrix, config_param_dict):
        def _drop_nan(df, should_row=False):
            df.replace("", np.nan, inplace=True)
            # empty row drop
            if should_row:
                df.dropna(how='all', inplace=True)
            # empty column drop
            df.dropna(axis=1, how='all', inplace=True)
            df.replace(np.nan, "", inplace=True)

        num_tabl = np.array(table_matrix)
        df = pd.DataFrame(num_tabl)
        _drop_nan(df, should_row=True)
        # Add numeric header for missing header column
        for i in range(len(df.columns)):
            if pd.isna(df.iloc[0, i]) or df.iloc[0, i] == '':
                df.iloc[0, i] = f'unnamed {i + 1}'
        if config_param_dict.get('col_header', {}).get('use_first_row'):
            df = df.reset_index(drop=True)
            col_header_row_index = 0
            # setting first row as column header
            df.columns = df.iloc[col_header_row_index]
            # dropping the first row
            df = df.iloc[pd.RangeIndex(len(df)).drop(col_header_row_index)]
            # df.columns = range(df.shape[1])
        json_data = json.loads(df.to_json(orient='records'))
        return df, df.to_html(header=False, index=False).replace('&lt;br&gt;', '<br>'), json_data, df.shape

    @classmethod
    def extract_custom_cells(cls, df, config_param_dict):
        custom_cells = config_param_dict.get("custom_cells")
        if not custom_cells:
            return None

        # if isinstance(df, list):
        #     df = cls.convert_matrix(df)[0]

        df_copy = df.copy(deep=True)
        df_copy.loc[-1] = df.columns
        df_copy = df_copy.sort_index().reset_index(drop=True)
        rows, cols = df_copy.shape
        final_body_arr = [[np.nan for x in range(cols)]
                          for y in range(rows)]
        table = df_copy.values
        for custom_row in custom_cells:
            row_range = cls.get_nums_from_range(
                custom_row.get("rows", ['0:']), rows-1)
            cell_range = cls.get_nums_from_range(
                custom_row.get("columns", ['0:']), cols-1)

            for row in row_range:
                for col in cell_range:
                    final_body_arr[row][col] = table[row][col]
        new_df = pd.DataFrame(final_body_arr)
        col_header_row_index = 0
        # setting first row as column header
        new_df.columns = df.columns
        # dropping the first row
        new_df = new_df.iloc[pd.RangeIndex(
            len(new_df)).drop(col_header_row_index)]
        new_df.dropna(axis=0, how="all", inplace=True)
        new_df.dropna(axis=1, how="all", inplace=True)
        new_df.fillna("((Not Extracted))", inplace=True)
        return json.loads(new_df.to_json(orient="records"))

    @classmethod
    def get_nums_from_range(cls, range_arr, n):
        try:
            range_nums = []
            range = range_arr[0]
            range = range if type(
                range) == str and ":" in range else int(range)
            if type(range) == str:
                num_arr = [int(num)
                           for num in range.split(":") if len(num) > 0]
                if bool(re.match(r'^-?[0-9]+\:{1}-?[0-9]+$', range)):
                    page_arr = cls._get_range_val(n+1)
                    if (num_arr[0] < 0 and num_arr[1] < 0) or (num_arr[0] > 0 and num_arr[1] > 0):
                        num_arr.sort()
                    # num_arr[0] = num_arr[0] if num_arr[0] >= 0 else num_arr[0]-1
                    # num_arr[1] = num_arr[1] if num_arr[1] > 0 else num_arr[1] + 1

                    range_nums += page_arr[num_arr[0]: num_arr[1]]
                elif bool(re.match(r'^-?[0-9]+\:{1}$', range)):
                    page_arr = cls._get_range_val(n)
                    range_nums += page_arr[num_arr[0]:]
                elif bool(re.match(r'^\:{1}-?[0-9]+$', range)):
                    page_arr = cls._get_range_val(n+1)
                    range_nums += page_arr[:num_arr[0]
                                           if num_arr[0] < 0 else num_arr[0]+1]
                else:
                    raise Exception
            elif range < 0:
                range_nums += [cls._get_range_val(n)[range]]
            elif range > 0:
                range_nums.append(range)
            else:
                raise Exception

            return range_nums
        except Exception as e:
            raise Exception(
                "Please provide valid 'row/cell range'. For example, specific page - [1] or range - [1:5] [6:-1] [-2:-1] or end to/start from [:5] [15:].")

    @classmethod
    def _get_range_val(cls, n, position=0):
        return [i for i in range(position, n+1)]
