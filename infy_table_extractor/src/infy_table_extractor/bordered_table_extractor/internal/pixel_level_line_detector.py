# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import math
import threading
from imageio import imread
from PIL import Image
import numpy as np
import cv2
from infy_table_extractor.bordered_table_extractor.internal.bordered_table_helper import TableHelper
from infy_table_extractor.bordered_table_extractor.internal.constants import *


class PixelLevelLineDetector:
    _line_img_list, _line_bbox_list = {}, {}

    @classmethod
    def image_with_lines(cls, rgb_matrix, image_matrix, horizontal_yn):

        border_matrix = []

        if (horizontal_yn is True):
            # Height
            axis_1 = len(rgb_matrix)
            # width
            axis_2 = len(rgb_matrix[0])
        else:
            # width
            axis_1 = len(rgb_matrix[0])
            # Height
            axis_2 = len(rgb_matrix)

        for i in range(axis_1):
            border_matrix_row = []
            for j in range(axis_2):
                if (i > 0):
                    if (horizontal_yn is True):
                        diff = cls.pixel_diff(
                            image_matrix[i][j], image_matrix[i-1][j])
                    else:
                        diff = cls.pixel_diff(
                            image_matrix[j][i], image_matrix[j][i-1])
                else:
                    diff = 0

                if (diff > DIFF_THRESHOLD):
                    diff = 255
                else:
                    diff = 0

                border_matrix_row.append(diff)

            border_matrix.append(border_matrix_row)

        if (horizontal_yn is True):
            border_matrix_final = border_matrix
        else:
            # Transpose matrix
            border_matrix_final = [[border_matrix[j][i] for j in range(
                len(border_matrix))] for i in range(len(border_matrix[0]))]

        return border_matrix_final

    @classmethod
    def compute_contrast_vector(cls, lines_matrix, horizontal_yn):
        result_vector = []

        convolution_size = L1_CONVOLUTION_SIZE
        line_portion = L1_CONTRAST_LINE_PORTION
        if (horizontal_yn is True):
            # Height
            axis_1 = len(lines_matrix)
            # width
            axis_2 = len(lines_matrix[0])
        else:
            # width
            axis_1 = len(lines_matrix[0])
            # Height
            axis_2 = len(lines_matrix)

        axis_2_portion = int(axis_2 * line_portion)
        for i in range(axis_1):
            icount = 0
            for j in range(axis_2_portion):
                found_contrast = 0
                for k in range(convolution_size):
                    if (i+k < axis_1):
                        if (horizontal_yn is True):
                            if (lines_matrix[i+k][j] == 255):
                                found_contrast = 1
                        else:
                            if (lines_matrix[j][i+k] == 255):
                                found_contrast = 1
                icount += found_contrast
            result_vector.append(icount/axis_2_portion)
        return result_vector

    @classmethod
    def find_best_orientation(
            cls, lines_matrix, current_i, axis_1, axis_2,
            horizontal_yn, contrast_method, RgbSkewDetectionMethod):
        jump_i = ORIENTATION_JUMP_I
        jump_steps = ORIENTATION_JUMP_STEPS
        convolution_size = L2_CONVOLUTION_SIZE
        max_contrast = 0.0

        for step in range((2*jump_steps)+1):
            m1_icount = 0
            m2_icount = 0
            i_val = 0
            m2_i_val = current_i

            for j in range(axis_2):
                i_val = int(
                    current_i + ((step - jump_steps) * j * jump_i / axis_2))
                if (i_val < 0):
                    i_val = 0
                if (i_val >= axis_1):
                    i_val = axis_1-1

                if(len(contrast_method) == 1 and
                    contrast_method[0] == RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD or
                        len(contrast_method) == 2):
                    # Method 1: match against convolution
                    m1_icount = cls.convolution_contrast_method(
                        horizontal_yn, lines_matrix, axis_1, convolution_size, i_val, j, m1_icount)

                if(len(contrast_method) == 1 and
                        contrast_method[0] == RgbSkewDetectionMethod.ADAPTIVE_CONTRAST_METHOD or
                        len(contrast_method) == 2):
                    # Method 2: adaptive matching where m2_i_val is flexible but conv size = 1
                    m2_icount = cls.adaptive_contrast_method(
                        horizontal_yn, lines_matrix, axis_1, m2_i_val,
                        i_val, step, jump_steps, j, m2_icount)

            if(len(contrast_method) == 1 and
                    contrast_method[0] == RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD or
                    len(contrast_method) == 2):
                m1_contrast_val = m1_icount/axis_2
                contrast_val = m1_contrast_val
            if(len(contrast_method) == 1 and
                    contrast_method[0] == RgbSkewDetectionMethod.ADAPTIVE_CONTRAST_METHOD or
                    len(contrast_method) == 2):
                m2_contrast_val = m2_icount/axis_2
                contrast_val = m2_contrast_val
            if(len(contrast_method) == 2):
                contrast_val = max(m1_contrast_val, m2_contrast_val)

            if (max_contrast < contrast_val):
                max_contrast = contrast_val
                i_end = i_val
        return max_contrast, i_end

    @classmethod
    def convolution_contrast_method(
            cls, horizontal_yn, lines_matrix, axis_1, convolution_size, i_val, j, m1_icount):
        m1_found_contrast = 0
        for k in range(convolution_size):
            if (i_val+k < axis_1):
                if (horizontal_yn is True):
                    if (lines_matrix[i_val+k][j] == 255):
                        m1_found_contrast = 1
                        break
                else:
                    if (lines_matrix[j][i_val+k] == 255):
                        m1_found_contrast = 1
                        break
        m1_icount += m1_found_contrast
        return m1_icount

    @classmethod
    def adaptive_contrast_method(
            cls, horizontal_yn, lines_matrix, axis_1, m2_i_val, i_val, step, jump_steps, j, m2_icount):
        m2_found_contrast = 0
        if (step - jump_steps != 0):
            step_direction = int(
                (step - jump_steps) / abs(step - jump_steps))
        else:
            step_direction = 0

        if (horizontal_yn is True):
            if (lines_matrix[m2_i_val][j] == 255):
                m2_found_contrast = 1
            else:
                if (m2_i_val + step_direction < axis_1) and (m2_i_val + step_direction > 0):
                    if ((lines_matrix[m2_i_val + step_direction][j] == 255) and
                            (abs(m2_i_val + step_direction - i_val) <= 1)):
                        m2_found_contrast = 1
                        m2_i_val = m2_i_val + step_direction
        else:
            if (lines_matrix[j][m2_i_val] == 255):
                m2_found_contrast = 1
            else:
                if (m2_i_val + step_direction < axis_1) and (m2_i_val + step_direction > 0):
                    if ((lines_matrix[j][m2_i_val + step_direction] == 255) and
                            (abs(m2_i_val + step_direction - i_val) <= 1)):
                        m2_found_contrast = 1
                        m2_i_val = m2_i_val + step_direction
        m2_icount += m2_found_contrast
        return m2_icount

    @classmethod
    def paint_lines(cls, lines_matrix, lines_detected, horizontal_yn):

        result_image_matrix = []

        if (horizontal_yn is True):
            # Height
            axis_1 = len(lines_matrix)
            # width
            axis_2 = len(lines_matrix[0])
        else:
            # width
            axis_1 = len(lines_matrix[0])
            # Height
            axis_2 = len(lines_matrix)

        current_counter = 0
        max_counter = len(lines_detected)

        for i in range(axis_1):
            if (lines_detected[current_counter][0] == i):
                pixel_val = 255
                if (current_counter < max_counter-1):
                    current_counter += 1
            else:
                pixel_val = 0

            result_image_matrix_axis_1 = []

            for _ in range(axis_2):
                result_image_matrix_axis_1.append(pixel_val)
            result_image_matrix.append(result_image_matrix_axis_1)

        if (horizontal_yn is True):
            result_image_matrix_final = result_image_matrix
        else:
            result_image_matrix_final = [[result_image_matrix[j][i] for j in range(
                len(result_image_matrix))] for i in range(len(result_image_matrix[0]))]

        return result_image_matrix_final

    @classmethod
    def detect_contrast_lines(cls, lines_matrix,
                              contrast_lines_vector, horizontal_yn,
                              contrast_method, RgbSkewDetectionMethod):

        lines_detected = []

        if (horizontal_yn is True):
            # Height
            axis_1 = len(lines_matrix)
            # width
            axis_2 = len(lines_matrix[0])
        else:
            # width
            axis_1 = len(lines_matrix[0])
            # Height
            axis_2 = len(lines_matrix)

        for i in range(axis_1):
            if (contrast_lines_vector[i] > L1_CONTRAST_THRESHOLD):
                max_contrast, i_end = cls.find_best_orientation(
                    lines_matrix, i, axis_1, axis_2, horizontal_yn,
                    contrast_method, RgbSkewDetectionMethod)

                if (max_contrast > L2_CONTRAST_THRESHOLD):

                    line = []
                    line.append(i)
                    line.append(i_end)
                    line.append(max_contrast)
                    lines_detected.append(line)
        return lines_detected

    @classmethod
    def rationalize_lines_detected(cls, lines_detected, horizontal_yn_flag):
        return_lines_detected = []
        prev_line_count = -100
        current_counter = -100
        current_contrast = -100
        last_line_pixel = lines_detected[len(lines_detected)-1][0]
        if (len(lines_detected) < 10):
            merge_distance = int(last_line_pixel/(5*len(lines_detected)))
        else:
            merge_distance = int(last_line_pixel/50)

        max_contrast = 0
        for i in range(len(lines_detected)):
            if (lines_detected[i][2] > max_contrast):
                max_contrast = lines_detected[i][2]

        # print("Rationalizing lines with distance: " +
        #       str(merge_distance) + " and contrast: " + str(max_contrast))
        high_contrast_lines = []
        if(horizontal_yn_flag is True):
            for i in range(len(lines_detected)):
                if (lines_detected[i][2] > max_contrast * 0.80):
                    high_contrast_lines.append(lines_detected[i])
        else:
            for i in range(len(lines_detected)):
                if (lines_detected[i][2] > max_contrast * 0.70):
                    high_contrast_lines.append(lines_detected[i])

        for i in range(len(high_contrast_lines)):
            line = high_contrast_lines[i]
            if (((prev_line_count + merge_distance) < line[0]) and (current_counter >= 0)):
                return_lines_detected.append(
                    high_contrast_lines[current_counter])
                current_counter = -100
                current_contrast = -100
            if ((line[2] > current_contrast)):
                current_counter = i
                current_contrast = line[2]
            prev_line_count = line[0]
        if (current_counter >= 0):
            return_lines_detected.append(high_contrast_lines[current_counter])

        return return_lines_detected

    @classmethod
    def pixel_diff(cls, pix_1, pix_2):
        r_diff = (abs(int(pix_1[0]) - int(pix_2[0])))**2
        g_diff = (abs(int(pix_1[1]) - int(pix_2[1])))**2
        b_diff = (abs(int(pix_1[2]) - int(pix_2[2])))**2

        diff = r_diff + g_diff + b_diff
        return diff/255

    @classmethod
    def detect_image_skew(cls, img, lines_detected):
        tot_skew, warning = 0, ""
        for line in lines_detected:
            tot_skew += line[1] - line[0]
        avg_skew = tot_skew / len(lines_detected)
        angle = math.degrees(math.atan(avg_skew/img.shape[1]))
        if(angle > 0.1):
            warning = "Skew detected: "+str(angle)
        return angle, warning

    @classmethod
    def detect_lines(cls, rgb_matrix, horizontal_yn_flag,
                     temp_folderpath, debug_mode_check, logger,
                     contrast_method, RgbSkewDetectionMethod):

        logger.debug(f"lines detection, horizontal = {horizontal_yn_flag}")
        # find size of the images
        image_height = len(rgb_matrix)
        image_width = len(rgb_matrix[0])
        # image_channels = len(rgb_matrix[0][0])

        # Create bitmap of matrix
        rgbArray = np.zeros((image_height, image_width, 3), 'uint8')

        np_image_matrix = np.asarray(rgb_matrix)
        image_matrix = np_image_matrix.tolist()

        lines_matrix = cls.image_with_lines(
            rgb_matrix, image_matrix, horizontal_yn_flag)
        contrast_lines_vector = cls.compute_contrast_vector(
            lines_matrix, horizontal_yn_flag)

        # for j in range(len(contrast_lines_vector)):
        #     logger.debug(str(j) + ":" + str(contrast_lines_vector[j]))
        # print("Finding lines: " + str(datetime.now().time()))
        logger.debug(f"Contrast lines detected: {len(contrast_lines_vector)}")
        lines_detected = cls.detect_contrast_lines(
            lines_matrix, contrast_lines_vector,
            horizontal_yn_flag, contrast_method, RgbSkewDetectionMethod)

        logger.debug(f"Skew lines detected: {len(lines_detected)}")
        # print("Rationalizing lines: " + str(datetime.now().time()))
        rationalized_lines_detected = cls.rationalize_lines_detected(
            lines_detected, horizontal_yn_flag)

        image_with_contrast_lines = cls.paint_lines(
            lines_matrix, rationalized_lines_detected, horizontal_yn_flag)
        rgbArray[..., 0] = image_with_contrast_lines
        rgbArray[..., 1] = image_with_contrast_lines
        rgbArray[..., 2] = image_with_contrast_lines
        logger.debug("rgb array:" + str(rgbArray.shape))

        img = Image.fromarray(rgbArray)
        img = np.array(img)

        if(debug_mode_check is True):
            if (horizontal_yn_flag is True):
                file_out_name = temp_folderpath + '/' + "rbg_hori.png"
            else:
                file_out_name = temp_folderpath + '/' + "rbg_vert.png"
            cv2.imwrite(file_out_name, img)
        PixelLevelLineDetector._line_img_list[horizontal_yn_flag], PixelLevelLineDetector._line_bbox_list[
            horizontal_yn_flag] = img, rationalized_lines_detected
        # return img, rationalized_lines_detected

    @classmethod
    def detect_all_cells(cls, img_file, within_bbox, temp_folderpath,
                         debug_mode_check, logger, config_param_dict, RgbSkewDetectionMethod):

        contrast_method = config_param_dict['rgb_line_skew_detection_method']
        deskew_image_reqd = config_param_dict['deskew_image_reqd']
        # read image
        rgb_matrix = imread(img_file)
        rgb_matrix = TableHelper.crop_image(rgb_matrix, within_bbox)

        logger.info("Line detection using RGBLineDetect started")
        thread1 = threading.Thread(target=cls.detect_lines, args=(
            rgb_matrix, True,
            temp_folderpath, debug_mode_check, logger, contrast_method, RgbSkewDetectionMethod))
        thread1.name = "thread_hor_line_detect"
        thread1.start()
        thread2 = threading.Thread(target=cls.detect_lines, args=(
            rgb_matrix, False,
            temp_folderpath, debug_mode_check, logger, contrast_method, RgbSkewDetectionMethod))
        thread2.name = "thread_ver_line_detect"
        thread2.start()
        thread1.join()
        thread2.join()
        logger.info("Line detection using RGBLineDetect completed")

        lines_detected = PixelLevelLineDetector._line_bbox_list[True]
        ver_img = PixelLevelLineDetector._line_img_list[False]
        hor_img = PixelLevelLineDetector._line_img_list[True]
        angle, warning = cls.detect_image_skew(
            rgb_matrix, lines_detected)

        if(deskew_image_reqd is True):
            rgb_matrix = TableHelper.deskew_image(rgb_matrix, angle)

        return TableHelper.get_cells_bbox(
            rgb_matrix.shape[0],
            rgb_matrix.shape[1], ver_img, hor_img, temp_folderpath,
            debug_mode_check, logger, 'pixel_level_line_detect'), warning, angle
