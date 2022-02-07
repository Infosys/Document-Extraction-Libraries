# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                        #
# ===============================================================================================================#

import math
import sys
import re
import bs4
import cv2
import pytesseract
import numpy as np
from infy_bordered_table_extractor.internal.bordered_table_helper import TableHelper


class OpencvLineDetector:

    @classmethod
    def detect_all_cells(cls, img, temp_folderpath,
                         debug_mode_check, logger, deskew_image_reqd,
                         process_hocr_reqd=False, process_adap_reqd=False):
        try:
            if(len(img.shape) == 3):
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if(process_hocr_reqd is True or process_adap_reqd is True):
                img_bin = cv2.adaptiveThreshold(
                    img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 35)  # 30
                img_bin = cv2.GaussianBlur(img_bin, (1, 1), 0)
            else:
                _, img_bin = cv2.threshold(
                    img, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            img_bin = 255-img_bin
            if(debug_mode_check is True):
                cv2.imwrite(temp_folderpath+"/" +
                            'img_bin.png', img_bin)

            angle, warning = cls.detect_image_skew(
                img, img_bin, temp_folderpath, debug_mode_check, logger)

            if(deskew_image_reqd is True):
                img_bin = TableHelper.deskew_image(img_bin, angle)
            if(process_hocr_reqd is True or process_adap_reqd is True):
                horizontal_lines, _ = cls.detect_horizontal_lines(
                    img, img_bin, temp_folderpath, debug_mode_check,
                    logger, 3, -1, process_hocr_reqd=process_hocr_reqd)

                vertical_lines, _ = cls.detect_vertical_lines(
                    img, img_bin, temp_folderpath, debug_mode_check,
                    logger, 3, -1, process_hocr_reqd=process_hocr_reqd)
            else:
                horizontal_lines, _ = cls.detect_horizontal_lines(
                    img, img_bin, temp_folderpath, debug_mode_check, logger,
                    process_hocr_reqd=process_hocr_reqd)

                vertical_lines, _ = cls.detect_vertical_lines(
                    img, img_bin, temp_folderpath, debug_mode_check,
                    logger, process_hocr_reqd=process_hocr_reqd)

            return TableHelper.get_cells_bbox(
                img.shape[0],
                img.shape[1], vertical_lines, horizontal_lines,
                temp_folderpath, debug_mode_check, logger, 'opencv_line_detect'), warning, angle
        except Exception as ex:
            _, _, tb = sys.exc_info()
            lineno = tb.tb_lineno
            raise Exception(str(ex)+" ((Line: "+str(lineno)+")")

    @classmethod
    def detect_vertical_lines(
            cls, img, img_bin, temp_folderpath, debug_mode_check,
            logger, MAXGAP=3, COMPARE_POS=0, process_hocr_reqd=False):
        try:
            # image with all vertical lines
            if(img.shape[0] <= 100):
                ver_kernel_len = 3
            elif(img.shape[0] <= 150):
                ver_kernel_len = img.shape[0]//25
            elif(img.shape[0] <= 500):
                ver_kernel_len = img.shape[0]//50
            elif(img.shape[0] <= 1500):
                ver_kernel_len = img.shape[0]//100
            else:
                ver_kernel_len = img.shape[0]//200
            ver_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (1, ver_kernel_len))
            if(process_hocr_reqd is True):
                image_1 = cv2.dilate(img_bin, ver_kernel, iterations=1)
                vertical_lines = cv2.erode(image_1, ver_kernel, iterations=1)
            else:
                image_1 = cv2.erode(img_bin, ver_kernel, iterations=2)
                vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=2)
            if(debug_mode_check is True):
                cv2.imwrite(temp_folderpath+"/" +
                            'image_v1.png', image_1)

            h_points = []
            # # vertical lines coordinate detection
            MIN_LINE_SCALE, threshold, minLineLength, maxLineGap = 0.4, 10, img.shape[
                0]//50, img.shape[1]//80
            rotated = TableHelper.rotate_image(vertical_lines, 90)
            edges = cv2.Canny(rotated, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
            if(lines is not None):
                for line in lines:
                    for x1, y1, x2, y2 in line:
                        if(x2-x1 > 0 and y1 == y2):
                            h_points.append([x1, y1, x2, y2, x2-x1])
            else:
                raise Exception(
                    "No cells detected: Vertical Lines not detected")
            h_points = sorted(h_points, key=lambda x: (x[1], x[0]))

            # Clustering lines into one with max pixel diff of 3
            if(len(h_points) == 0):
                raise Exception(
                    "No cells detected: Vertical Lines not detected")
            h_grouped = cls.cluster(
                h_points, MAXGAP, 1, 2, 0, COMPARE_POS)
            horizontal_lines = np.zeros((img.shape[1], img.shape[0]), np.uint8)
            horizontal_lines.fill(255)
            actual_h_points, actual_h_grouped = [], []
            # for each clustered line, finds the total width of line
            # and if greater than 40% of total image width it draws a
            #  complete line on the horizontal_lines image
            for group in h_grouped:
                line_height, count = 0, 0
                for line in group:
                    # if any line is greater than 10% of the image width,
                    #  then consider it as potential line
                    if(line[4] > 0.05*img.shape[0]):
                        count += 1
                    line_height += line[4]
                if(line_height >= MIN_LINE_SCALE * img.shape[0] and count > 0):
                    actual_h_grouped.append(group)
                    actual_h_points.append(
                        [0, group[0][1], img.shape[0], group[0][3]])
                    cv2.line(
                        horizontal_lines, (0, group[0][1]), (img.shape[0], group[0][3]), (0, 0, 0), 2)
            vertical_lines = TableHelper.rotate_image(
                horizontal_lines, 270)

            if(debug_mode_check is True):
                cv2.imwrite(temp_folderpath+"/" +
                            'image_v_re-drawn.png', vertical_lines)
            return vertical_lines, actual_h_grouped
            # return vertical_lines, actual_v_grouped
        except Exception as ex:
            _, _, tb = sys.exc_info()
            lineno = tb.tb_lineno
            raise Exception(str(ex)+" ((Line: "+str(lineno)+")")

    @classmethod
    def detect_horizontal_lines(cls, img,
                                img_bin, temp_folderpath, debug_mode_check,
                                logger, MAXGAP=3, COMPARE_POS=0, process_hocr_reqd=False):
        try:

            # image with all horizontal lines
            if(img.shape[1] <= 100):
                hor_kernel_len = 3
            elif(img.shape[1] < 150):
                hor_kernel_len = img.shape[1]//25
            elif(img.shape[1] <= 500):
                hor_kernel_len = img.shape[1]//50
            elif(img.shape[1] <= 1500):
                hor_kernel_len = img.shape[1]//100
            else:
                hor_kernel_len = img.shape[1]//200

            hor_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (hor_kernel_len, 1))
            if(process_hocr_reqd is True):
                image_2 = cv2.dilate(img_bin, hor_kernel, iterations=1)
                horizontal_lines = cv2.erode(image_2, hor_kernel, iterations=1)
            else:
                image_2 = cv2.erode(img_bin, hor_kernel, iterations=2)
                horizontal_lines = cv2.dilate(
                    image_2, hor_kernel, iterations=2)

            if(debug_mode_check is True):
                cv2.imwrite(temp_folderpath+"/" +
                            'image_h1.png', image_2)
            h_points = []
            MIN_LINE_SCALE, threshold, minLineLength, maxLineGap = 0.4, 10, img.shape[
                0]//50, img.shape[1]//80
            edges = cv2.Canny(horizontal_lines, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
            if(lines is None):
                raise Exception("No cells found: Horizontal line not detected")
            for line in lines:
                for x1, y1, x2, y2 in line:
                    if(x2-x1 > 0 and y1 == y2):
                        h_points.append([x1, y1, x2, y2, x2-x1])
            # h_points.sort(key=lambda x: x[1])
            h_points = sorted(h_points, key=lambda x: (x[1], x[0]))
            # Clustering lines into one with max pixel diff of 3
            if(len(h_points) == 0):
                raise Exception(
                    "No cells detected: Horizontal Lines not detected")
            h_grouped = cls.cluster(
                h_points, MAXGAP, 1, 2, 0, COMPARE_POS)
            horizontal_lines = np.zeros((img.shape[0], img.shape[1]), np.uint8)
            horizontal_lines.fill(255)
            actual_h_points, actual_h_grouped = [], []
            # for each clustered line, finds the total width of line
            # and if greater than 40% of total image width it draws a complete line on the horizontal_lines image
            for group in h_grouped:
                line_height, count = 0, 0
                for line in group:
                    # if any line is greater than 10% of the image width, then consider it as potential line
                    if(line[4] > 0.05*img.shape[1]):
                        count += 1
                    line_height += line[4]
                if(line_height >= MIN_LINE_SCALE * img.shape[1] and count > 0):
                    actual_h_grouped.append(group)
                    actual_h_points.append(
                        [0, group[0][1], img.shape[1], group[0][3]])
                    cv2.line(
                        horizontal_lines, (0, group[0][1]), (img.shape[1], group[0][3]), (0, 0, 0), 2)
            if(debug_mode_check is True):
                cv2.imwrite(temp_folderpath+"/" +
                            'image_h_re-drawn.png', horizontal_lines)
            return horizontal_lines, actual_h_grouped
        except Exception as ex:
            _, _, tb = sys.exc_info()
            lineno = tb.tb_lineno
            raise Exception(str(ex)+" ((Line: "+str(lineno)+")")

    @classmethod
    def cluster(cls, data, maxgap, position, position_1, position_2, compare_pos):
        '''Arrange data into groups where successive elements
       differ by no more than *maxgap*'''
        groups = [[data[0]]]
        for x in data[1:]:
            if abs(x[position] - groups[-1][compare_pos][position]) <= maxgap:
                if not (groups[-1][-1][position_2] <= x[position_2] <= (groups[-1][-1][position_2]+groups[-1][-1][4]) and groups[-1][-1][position_2] <= x[position_1] <= (groups[-1][-1][position_2]+groups[-1][-1][4])):
                    groups[-1].append(x)
            else:
                groups.append([x])
        return groups

    @classmethod
    def line_detection_by_hocr(cls, text_extract_provider, img, temp_folderpath, debug_mode_check, logger, deskew_image_reqd):
        img_arr = img
        if(len(img.shape) == 2):
            img_arr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        word_structure = text_extract_provider.get_tokens(1, img_arr)

        height_sum, word_count = 0, 0
        for word_dict in word_structure:
            if(word_dict['text'] != '' and re.search("^[^[|(]{1}", word_dict['text'])):
                height_sum += word_dict['bbox'][3]
                word_count += 1
                x, y, w, h = word_dict['bbox'][0], word_dict['bbox'][1], \
                    word_dict['bbox'][2], word_dict['bbox'][3]
                img_arr[y:y+h, x:x+w] = (255, 255, 255)
        cv2.imwrite(
            f'{temp_folderpath}/_removed_text.png', img_arr)
        mean_word_h = height_sum/word_count if word_count > 0 else 0
        box, warning, deskew_angle = cls.detect_all_cells(
            img_arr, temp_folderpath, debug_mode_check, logger, deskew_image_reqd, True)
        return box, True, mean_word_h, warning, deskew_angle

    @classmethod
    def detect_image_skew(cls, img, img_bin, temp_folderpath, debug_mode_check, logger):
        warning, angle = "", 0
        _, actual_h_grouped = cls.detect_horizontal_lines(
            img, img_bin, temp_folderpath, debug_mode_check, logger,  1, -1, process_hocr_reqd=False)
        if(actual_h_grouped is not None):
            start = 2 if len(actual_h_grouped) > 3 else 0
            px_diff_arr = [actual_h_grouped[i][-1][1] -
                           actual_h_grouped[i][0][1] for i in range(start, len(actual_h_grouped))]
            px_diff = round(sum(px_diff_arr)/len(px_diff_arr))
            px_diff = px_diff-1 if px_diff > 0 else px_diff
            angle = math.degrees(math.atan(px_diff/img.shape[1]))
            angle_dir_arr = [actual_h_grouped[i][-1][0] > actual_h_grouped[i][0][0]
                             for i in range(start, len(actual_h_grouped))]
            count = 0
            for vote in angle_dir_arr:
                if(vote is True):
                    count += 1
            angle = angle if(count > len(angle_dir_arr)/2) else -angle
            if(angle > 0.1):
                warning = "Skew detected: "+str(angle)
        else:
            warning = "Skew cannot be detected"
        return angle, warning
