# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import copy
import shutil
import concurrent.futures
from datetime import datetime
import numpy as np
import cv2
from infy_table_extractor.bordered_table_extractor.internal.pixel_level_line_detector import PixelLevelLineDetector
from infy_table_extractor.bordered_table_extractor.internal.bordered_table_helper import TableHelper
from infy_table_extractor.bordered_table_extractor.internal.opencv_line_detector import OpencvLineDetector
from infy_table_extractor.bordered_table_extractor.internal.pixel_parser import PixelParser


class ImageTableBorderReader:
    """
    This is a class to convert table with border information in images to excel file.
    """

    def __init__(self, table_detection_provider, cell_extraction_provider,
                 temp_folderpath, logger, debug_mode_check, LineDetectionMethod,
                 RgbSkewDetectionMethod, OutputFileFormat):
        """
        The constructor for image_table_border_detection class.
        """
        self.table_detection_provider = table_detection_provider
        self.cell_extraction_provider = cell_extraction_provider
        self.logger = logger
        self.debug_mode_check = debug_mode_check
        self.temp_folderpath = temp_folderpath
        self.LineDetectionMethod = LineDetectionMethod
        self.RgbSkewDetectionMethod = RgbSkewDetectionMethod
        self.OutputFileFormat = OutputFileFormat
        self._text_dict = []
        self.processing_msg = []

    def extract(self, img_file, file_data_list, within_bbox, config_param_dict):
        """
        The function to extract information from the images.

        Parameters:
            img : image
            img_name: image file name
            save_folder_path: Path to save the excel file
        Returns:
        box, bitnot = self._detect_all_cells(img, img_name)
            json response of the extracted table
            error
        """
        warnings = []
        org_img = cv2.imread(img_file)
        method = config_param_dict['line_detection_method']
        img_name = os.path.splitext(os.path.split(img_file)[1])[0]
        if config_param_dict['auto_detect_border']:
            within_bbox = TableHelper.detect_table_border(
                img_file, within_bbox)
        crop_img = TableHelper.crop_image(org_img, within_bbox)
        temp_folderpath = self.temp_folderpath
        temp_folderpath = TableHelper.make_dir_with_timestamp(
            temp_folderpath, img_name)
        if(self.debug_mode_check is True):
            cv2.imwrite(f'{temp_folderpath}/img.png', crop_img)

        process_hocr_reqd, mean_word_h = False, 0
        if(len(method) == 1 and method[0] == self.LineDetectionMethod.RGB_LINE_DETECT):
            try:
                self.processing_msg.append("Line detection using RGB matrix")
                box, warning, deskew_angle = PixelLevelLineDetector.detect_all_cells(
                    img_file, within_bbox, temp_folderpath, self.debug_mode_check,
                    self.logger, config_param_dict, self.RgbSkewDetectionMethod)
            except Exception as ex:
                self.processing_msg.append("RGB matrix failed due to "+str(ex))
                try:
                    box, process_hocr_reqd, mean_word_h, warning, deskew_angle = \
                        self._opencv_line_detection(
                            crop_img, temp_folderpath, config_param_dict['deskew_image_reqd'])
                except Exception as ex:
                    raise Exception(str(self.processing_msg))
        elif(len(method) == 1 and method[0] == self.LineDetectionMethod.OPENCV_LINE_DETECT):
            try:
                box, process_hocr_reqd, mean_word_h, warning, deskew_angle = self._opencv_line_detection(
                    crop_img, temp_folderpath, config_param_dict['deskew_image_reqd'])
            except Exception as ex:
                try:
                    self.processing_msg.append(
                        "Line detection using RGB matrix")
                    box, warning, deskew_angle = PixelLevelLineDetector.detect_all_cells(
                        img_file, within_bbox, temp_folderpath, self.debug_mode_check,
                        self.logger, config_param_dict, self.RgbSkewDetectionMethod)
                except Exception as ex:
                    raise Exception(str(self.processing_msg))
        else:
            box, process_hocr_reqd, mean_word_h, warning, deskew_angle = self._evaluate_all_methods(
                crop_img, img_file, within_bbox, temp_folderpath, config_param_dict['deskew_image_reqd'])

        warnings.append(TableHelper.check_image_dpi(img_file))
        if(warning != ''):
            warnings.append(warning)
        row, countcol = self._get_table_structure(
            box, process_hocr_reqd, mean_word_h)

        org_img = TableHelper.deskew_image(org_img, deskew_angle) if(
            config_param_dict['deskew_image_reqd'] is True) else org_img

        arr, false_r_count = self._extract_text_from_cells(
            org_img, within_bbox, row, config_param_dict, temp_folderpath, file_data_list)
        self.processing_msg.append(
            {'no_of_rows': len(row)-false_r_count, 'no_of_columns': countcol})
        try:
            body_arr, header_arr, warnings = self._get_table_header_and_body(
                arr, countcol, false_r_count, row, config_param_dict, warnings)
        except Exception:
            arr, false_r_count = self._extract_text_from_cells(
                org_img, within_bbox, row, config_param_dict, temp_folderpath, file_data_list, False)
            body_arr, header_arr, warnings = self._get_table_header_and_body(
                arr, countcol, false_r_count, row, config_param_dict, warnings)
        processing_msg = self.processing_msg
        self.processing_msg = []
        if self.debug_mode_check is False:
            shutil.rmtree(temp_folderpath)
        return TableHelper.generate_excel_and_json(
            img_name, body_arr, header_arr, config_param_dict['output'], self.OutputFileFormat, self.logger), \
            warnings, processing_msg, os.path.abspath(temp_folderpath)

    def _get_table_structure(self, box, process_hocr_reqd, mean_word_h):

        mean = sum([box[i][3] for i in range(len(box))])//len(box)
        box.sort(key=lambda x: (x[1], x[0]))
        row, column = [], []
        for i in range(len(box)):
            if(i == 0):
                column.append(box[i])
                previous = box[i]
            else:
                if(box[i][1] == previous[1]):
                    column.append(box[i])
                    previous = box[i]
                else:
                    row.append(column)
                    column = []
                    previous = box[i]
                    column.append(box[i])
        row.append(column)

        self.logger.debug("column: {}".format(column))
        self.logger.debug("row: {}".format(row))

        if row[0][0][3] < mean//5:
            row.remove(row[0])

        if(process_hocr_reqd is True):
            # remove rows where row height is less than word height
            remove_row = []
            for i in range(len(row)):
                if row[i][0][3] < mean_word_h - mean_word_h/4:
                    remove_row.append(row[i])
            row = [x for x in row if x not in remove_row]

        countcol = len(row[0])
        for i in range(len(row)):
            if countcol < len(row[i]):
                countcol = len(row[i])
        return row, countcol

    def _opencv_line_detection(self, img, temp_folderpath, deskew_image_reqd):
        img_arr = copy.deepcopy(img)
        process_hocr_reqd, mean_word_h = False, 0
        try:
            self.processing_msg.append(
                "Line detection using Adaptive threshold")
            box, warning, deskew_angle = OpencvLineDetector.detect_all_cells(
                img_arr, temp_folderpath, self.debug_mode_check, self.logger,
                deskew_image_reqd, process_hocr_reqd=False, process_adap_reqd=True)
        except Exception as ex:
            self.processing_msg.append("Adaptive threshold failed:" + str(ex))
            try:
                self.processing_msg.append(
                    "Line detection using normal threshold")
                box, warning, deskew_angle = OpencvLineDetector.detect_all_cells(
                    img_arr, temp_folderpath, self.debug_mode_check, self.logger, deskew_image_reqd)
            except Exception as ex:
                self.processing_msg.append(
                    "Normal threshold failed:" + str(ex))
                try:
                    self.processing_msg.append(
                        "Line detection using HOCR and adaptive threshold")
                    box, process_hocr_reqd, mean_word_h, warning, deskew_angle = \
                        OpencvLineDetector.line_detection_by_hocr(
                            self.table_detection_provider, img_arr, temp_folderpath,
                            self.debug_mode_check, self.logger, deskew_image_reqd)
                except Exception as ex:
                    self.processing_msg.append("HOCR failed:" + str(ex))
                    raise Exception
        return box, process_hocr_reqd, mean_word_h, warning, deskew_angle

    def _evaluate_all_methods(self, img, img_file, within_bbox, temp_folderpath,
                              deskew_image_reqd):
        try:
            opencv_box, process_hocr_reqd, mean_word_h, warning, deskew_angle = self._opencv_line_detection(
                img, temp_folderpath, deskew_image_reqd)
        except Exception:
            opencv_box = []
        try:
            self.processing_msg.append("Line detection using RGB matrix")
            rgb_box, warning, deskew_angle = PixelLevelLineDetector.detect_all_cells(
                img_file, within_bbox, temp_folderpath, self.debug_mode_check,
                self.logger, deskew_image_reqd, self.RgbSkewDetectionMethod)
        except Exception:
            rgb_box = []
        if(opencv_box == [] and rgb_box == []):
            raise Exception("No cells detected")
        else:
            if(len(opencv_box) >= len(rgb_box)):
                self.processing_msg.append(
                    "Chosen method of Line detection: OPENCV_LINE_DETECT")
                return opencv_box, process_hocr_reqd, mean_word_h, warning, deskew_angle
            else:
                self.processing_msg.append(
                    "Chosen method of Line detection: RGB_LINE_DETECT")
                return rgb_box, False, 0, warning, deskew_angle

    def _get_table_header_and_body(self, arr, countcol, false_r_count,
                                   row, config_param_dict, warnings):
        if config_param_dict['col_header']['use_first_row'] is True:
            header_arr = arr[:countcol].tolist()
            for i, header in enumerate(header_arr):
                j = 1
                for k, header_2 in enumerate(header_arr):
                    if(i != k):
                        if header == header_2 and header != ' ':
                            header_arr[k] = header_2+str(j)
                            j += 1
                        elif header == header_2 and header_2 == ' ':
                            header_arr[k] = "col_" + str(j+1)
                            j += 1
                if(header == ' '):
                    header_arr[i] = "col_1"
            body_arr = arr[countcol:]
            body_arr = body_arr.reshape(
                len(row)-1-false_r_count, countcol)

        else:
            header_arr = config_param_dict['col_header'].get('values')
            if len(header_arr) > 0:
                if len(header_arr) - len(arr) > 0:
                    warn = 'Header arr length provided is more than the column extracted'
                    warnings.append(warn)
                    self.logger.warning(warn)
                    header_arr = [f'col_{i+1}' for i in range(countcol)]
                elif len(arr) - len(header_arr) > 0:
                    extra_header_arr = [
                        f'col_{i+1}' for i in range(countcol - len(header_arr))]
                    header_arr = header_arr + extra_header_arr
            else:
                header_arr = [f'col_{i+1}' for i in range(countcol)]
            body_arr = arr.reshape(
                len(row)-false_r_count, countcol)

        if len(config_param_dict['custom_cells']) == 0 or \
            (len(config_param_dict['custom_cells']) == 1 and
             config_param_dict['custom_cells'][0].get('columns') == [] and
             config_param_dict['custom_cells'][0].get('rows') == []):
            pass
        else:
            header_arr.insert(0, '__rownum')
            body_arr = body_arr.tolist()
            for i, row in enumerate(body_arr):
                row.insert(0, i+1)
            countcol += 1
            body_arr, header_arr = self._extract_custom_cells(
                config_param_dict['custom_cells'], body_arr, header_arr, countcol)

        return body_arr, header_arr, warnings

    def _extract_custom_cells(self, custom_cells, body_arr, header_arr, countcol):
        all_col_num = [col for col in range(countcol-1)]
        all_row_num = [row for row in range(len(body_arr)+1)]
        final_body_arr, final_header_arr = [], [
            '((Not Extracted))' for c in range(0, countcol)]
        for _ in body_arr:
            final_body_arr.append(
                ['((Not Extracted))' for c in range(0, countcol)])
        final_header_arr[0] = header_arr[0]
        for row_column in custom_cells:
            if(row_column.get('rows') is not None):
                row_list = self._get_all_numbers_from_range_list(
                    row_column['rows'], all_row_num)
            else:
                row_list = self._get_all_numbers_from_range_list(
                    ['0:'], all_row_num)
            if(row_column.get('columns') is not None):
                column_list = self._get_all_numbers_from_range_list(
                    row_column['columns'], all_col_num)
            else:
                column_list = self._get_all_numbers_from_range_list(
                    ['0:'], all_col_num)
            for col in range(len(column_list)):
                column_list[col] += 1
            for row in range(len(row_list)):
                row_list[row] -= 1
            column_list.insert(0, 0)
            for col in column_list:
                final_header_arr[col] = header_arr[col]

            for row in row_list:
                for col in column_list:
                    final_body_arr[row][col] = body_arr[row][col]

        remove_row, remove_col = [], []
        for row in range(len(final_body_arr)):
            count = 0
            for col in range(len(final_body_arr[row])):
                if(final_body_arr[row][col] == '((Not Extracted))'):
                    count += 1
            if(count == len(final_body_arr[row])):
                remove_row.append(final_body_arr[row])
        final_body_arr = [x for x in final_body_arr if x not in remove_row]
        for col in range(1, countcol):
            count = 0
            for row in range(len(final_body_arr)):
                if(final_body_arr[row][col] == '((Not Extracted))'):
                    count += 1
            if(count == len(final_body_arr)):
                remove_col.append(col)
        for i, col in enumerate(remove_col):
            for row in range(len(final_body_arr)):
                final_body_arr[row].pop(col)
            final_header_arr.pop(col)
            if(len(remove_col) > i+1):
                for j in range(i+1, len(remove_col)):
                    remove_col[j] -= 1

        return final_body_arr, final_header_arr

    def _get_all_numbers_from_range_list(self, num_range_list, num_list):
        try:
            numbers = []
            for num in num_range_list:
                num = num if isinstance(num, str) and ":" in num else int(num)
                if isinstance(num, str):
                    num_arr = num.split(":")
                    if(len(num_arr) == 2 and '' not in num_arr):
                        numbers += num_list[int(num_arr[0]):int(num_arr[1])]
                    elif(len(num_arr) == 2 and '' in num_arr):
                        numbers += num_list[int(num_arr[0]):] \
                            if num[-1] == ":" else num_list[:int(num_arr[1])]
                    else:
                        raise Exception
                else:
                    numbers.append(num_list[num])
            return numbers
        except Exception:
            raise Exception(
                ("Please provide valid number range. For example, specific - [1,7] "
                 "or range - [7:9,18,29] or end to/start from [:5,15:]."))

    def _extract_text_from_cells(self, org_img, within_bbox, finalboxes,
                                 config_param_dict, temp_folderpath, file_data_list, if_threading=True):
        self.logger.debug("Start time for text extraction: " +
                          datetime.now().strftime("%Y%m%d-%H%M%S"))
        finalboxes = self._get_real_coordinates(finalboxes, within_bbox)
        if config_param_dict['image_cell_cleanup_reqd'] is False or if_threading is False:
            if if_threading is False:
                self.processing_msg.append(
                    'Text extraction without threading, as threading failed')
            for i in range(len(finalboxes)):
                self._cell_text_extraction(
                    org_img, file_data_list, config_param_dict, temp_folderpath, finalboxes, i)

        else:
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=10,
                    thread_name_prefix="thread_text_extract") as executor:
                self.processing_msg.append('Text extraction with threading')
                thread_pool_dict = {
                    executor.submit(
                        self._cell_text_extraction, org_img,
                        file_data_list, config_param_dict, temp_folderpath, finalboxes, i): i
                    for i in range(len(finalboxes))
                }
                futures = {}
                for future in concurrent.futures.as_completed(thread_pool_dict):
                    i = thread_pool_dict[future]
                    futures[i] = future

        self.logger.debug("End time for text extraction: " +
                          datetime.now().strftime("%Y%m%d-%H%M%S"))

        outer, false_r_count = [], 0
        self._text_dict.sort(key=lambda x: (
            x['cell_bbox'][1], x['cell_bbox'][0]))
        y, count, col = self._text_dict[0]['cell_bbox'][1], 0, len(
            finalboxes[0])
        for t in self._text_dict:
            outer.append(t['cell_text'])
            if t['cell_bbox'][1] == y and t['cell_text'] == '':
                count += 1
            else:
                count = 0
                y = t['cell_bbox'][1]
            if count == col:
                outer = outer[0:len(outer)-count]
                false_r_count += 1
        arr = np.array(outer)
        self._text_dict = []
        return arr, false_r_count

    def _cell_text_extraction(self, img, file_data_list, config_param_dict, temp_folderpath, finalboxes, i):

        img_pre_processs_list, additional_cell_info, cell_bbox_list = [], [], []
        for j in range(len(finalboxes[i])):
            y, x, w, h = finalboxes[i][j][0], finalboxes[i][j][1], finalboxes[i][j][2], finalboxes[i][j][3]
            finalimg = img[x:x+h, y:y+w]
            cell_id = f'{y}_{x}_{w}_{h}'
            self.logger.debug(
                "text extraction for cell bbox: {}".format((y, x, w, h)))
            if config_param_dict['image_cell_cleanup_reqd'] is True:
                finalimg, px_converted = PixelParser.preprocess_image(
                    finalimg, f'{temp_folderpath}/cell_{i}_{j}', self.debug_mode_check)
            else:
                px_converted = 'org'
            self.logger.debug(
                f"cell_{i}_{j} pre-processing completed")
            additional_cell_info.append(
                {'cell_id': cell_id,
                 'cell_img_path': os.path.abspath(f'{temp_folderpath}/cell_{i}_{j}_final.png'),
                 'cell_bbox': [y, x, w, h],
                 'cell_img': finalimg})
            cell_bbox_list.append({
                'cell_id': cell_id,
                'cell_bbox': [y, x, w, h]})
            img_pre_processs_list.append(
                {'if_org': px_converted,
                 'cell_bbox': [y, x, w, h]}
            )
            cv2.imwrite(additional_cell_info[j]
                        ['cell_img_path'], finalimg)
        additional_info = {'cell_info': additional_cell_info}
        result = self.cell_extraction_provider.get_text(
            img, cell_bbox_list, file_data_list, additional_info, temp_folderpath)
        additional_cell_info_2 = []
        for i, res in enumerate(result):
            if res['cell_text'] == '' and \
                    res['cell_bbox'] == img_pre_processs_list[i]['cell_bbox'] and \
                    img_pre_processs_list[i]['if_org'] != 'org':
                cell_id = additional_info['cell_info'][i]['cell_id']
                finalimg = 255 - \
                    additional_info['cell_info'][i]['cell_img']
                y, x, w, h = additional_info['cell_info'][i]['cell_bbox']
                cv2.imwrite(
                    f'{temp_folderpath}/cell_{y}_{x}_invert.png', finalimg)
                additional_cell_info_2.append(
                    {'cell_id': cell_id,
                     'cell_img_path': os.path.abspath(f'{temp_folderpath}/cell_{y}_{x}_invert.png'),
                     'cell_bbox': [y, x, w, h],
                     'cell_img': finalimg}
                )
            else:
                self._text_dict.append(res)
        if len(additional_cell_info_2) > 0:
            self._text_dict += self.cell_extraction_provider.get_text(
                img, file_data_list, {'cell_info': additional_cell_info_2}, temp_folderpath)
        self.logger.debug(
            f"cell_{i}_{j} text extraction completed")

    def _get_real_coordinates(self, bboxes, within_bbox):
        finalboxes = []
        if not within_bbox:
            return bboxes
        for row in range(len(bboxes)):
            rows = []
            for col in range(len(bboxes[row])):
                rows.append([bboxes[row][col][0]+within_bbox[0],
                             bboxes[row][col][1]+within_bbox[1],
                             bboxes[row][col][2],
                             bboxes[row][col][3]])
            finalboxes.append(rows)
        return finalboxes
