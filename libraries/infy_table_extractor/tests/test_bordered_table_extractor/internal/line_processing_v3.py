# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import json
import os
import numpy as np
from PIL import Image
from datetime import datetime
from imageio import imread
from tempfile import NamedTemporaryFile
import shutil
import csv
import glob
import cv2


def image_with_lines(rgb_matrix, image_matrix, horizontal_yn, dict_config):

    DIFF_THRESHOLD = float(dict_config.get("PIXEL_DIFF_THRESHOLD"))
    border_matrix = []

    if (horizontal_yn == True):
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
                if (horizontal_yn == True):
                    diff = pixel_diff(image_matrix[i][j], image_matrix[i-1][j])
                else:
                    diff = pixel_diff(image_matrix[j][i], image_matrix[j][i-1])
            else:
                diff = 0

            if (diff > DIFF_THRESHOLD):
                diff = 255
            else:
                diff = 0

            border_matrix_row.append(diff)

        border_matrix.append(border_matrix_row)

    if (horizontal_yn == True):
        border_matrix_final = border_matrix
    else:
        # Transpose matrix
        border_matrix_final = [[border_matrix[j][i] for j in range(
            len(border_matrix))] for i in range(len(border_matrix[0]))]

    return border_matrix_final


def compute_contrast_vector(lines_matrix, horizontal_yn, dict_config):
    result_vector = []

    convolution_size = int(dict_config.get("L1_CONVOLUTION_SIZE"))
    line_portion = float(dict_config.get("L1_CONTRAST_LINE_PORTION"))
    if (horizontal_yn == True):
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
                    if (horizontal_yn == True):
                        if (lines_matrix[i+k][j] == 255):
                            found_contrast = 1
                    else:
                        if (lines_matrix[j][i+k] == 255):
                            found_contrast = 1
            icount += found_contrast
        result_vector.append(icount/axis_2_portion)
    return result_vector


def find_best_orientation(lines_matrix, current_i, axis_1, axis_2, horizontal_yn, dict_config):
    jump_i = int(dict_config.get("ORIENTATION_JUMP_SIZE"))
    jump_steps = int(dict_config.get("ORIENTATION_JUMP_STEPS"))
    convolution_size = int(dict_config.get("L2_CONVOLUTION_SIZE"))
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

            # Method 1: match against convolution
            m1_found_contrast = 0
            for k in range(convolution_size):
                if (i_val+k < axis_1):
                    if (horizontal_yn == True):
                        if (lines_matrix[i_val+k][j] == 255):
                            m1_found_contrast = 1
                    else:
                        if (lines_matrix[j][i_val+k] == 255):
                            m1_found_contrast = 1
            m1_icount += m1_found_contrast

            # Method 2: adaptive matching where m2_i_val is flexible but conv size = 1
            m2_found_contrast = 0
            if (step - jump_steps != 0):
                step_direction = int(
                    (step - jump_steps) / abs(step - jump_steps))
            else:
                step_direction = 0

            if (horizontal_yn == True):
                if (lines_matrix[m2_i_val][j] == 255):
                    m2_found_contrast = 1
                else:
                    if (m2_i_val + step_direction < axis_1) and (m2_i_val + step_direction > 0):
                        if ((lines_matrix[m2_i_val + step_direction][j] == 255) and (abs(m2_i_val + step_direction - i_val) <= 1)):
                            m2_found_contrast = 1
                            m2_i_val = m2_i_val + step_direction
            else:
                if (lines_matrix[j][m2_i_val] == 255):
                    m2_found_contrast = 1
                else:
                    if (m2_i_val + step_direction < axis_1) and (m2_i_val + step_direction > 0):
                        if ((lines_matrix[j][m2_i_val + step_direction] == 255) and (abs(m2_i_val + step_direction - i_val) <= 1)):
                            m2_found_contrast = 1
                            m2_i_val = m2_i_val + step_direction
            m2_icount += m2_found_contrast

        m1_contrast_val = m1_icount/axis_2
        m2_contrast_val = m2_icount/axis_2
        contrast_val = max(m1_contrast_val, m2_contrast_val)
        ##print("Pixel: " + str(current_i) + " i_val : " + str(i_val) + " m1_contrast: " + str(m1_contrast_val) + " m2_contrast: " + str(m2_contrast_val))

        if (max_contrast < contrast_val):
            max_contrast = contrast_val
            i_end = i_val
    # print("Pixel: " + str(current_i) + " i_val : " + str(i_end) + " contrast : " + str(max_contrast))
    return max_contrast, i_end


def paint_lines(lines_matrix, lines_detected, horizontal_yn, dict_config):

    result_image_matrix = []

    if (horizontal_yn == True):
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

        for j in range(axis_2):
            result_image_matrix_axis_1.append(pixel_val)
        result_image_matrix.append(result_image_matrix_axis_1)

    if (horizontal_yn == True):
        result_image_matrix_final = result_image_matrix
    else:
        result_image_matrix_final = [[result_image_matrix[j][i] for j in range(
            len(result_image_matrix))] for i in range(len(result_image_matrix[0]))]

    return result_image_matrix_final


def detect_contrast_lines(lines_matrix, contrast_lines_vector, horizontal_yn, dict_config):

    L1_CONTRAST_THRESHOLD = float(dict_config.get("L1_CONTRAST_THRESHOLD"))
    L2_CONTRAST_THRESHOLD = float(dict_config.get("L2_CONTRAST_THRESHOLD"))

    lines_detected = []

    if (horizontal_yn == True):
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
            max_contrast, i_end = find_best_orientation(
                lines_matrix, i, axis_1, axis_2, horizontal_yn, dict_config)
    # print("##" + str(i) + " End:" + str(i_end) + " Max:" + str(max_contrast) + "L1:" + str(contrast_lines_vector[i]) )
            if (max_contrast > L2_CONTRAST_THRESHOLD):
                # print("##" + str(i) + " End:" + str(i_end) + " Max:" + str(max_contrast) + "L1:" + str(contrast_lines_vector[i]) )

                line = []
                line.append(i)
                line.append(i_end)
                line.append(max_contrast)
                lines_detected.append(line)
    return lines_detected


def rationalize_lines_detected(lines_detected):
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

    print("Rationalizing lines with distance: " +
          str(merge_distance) + " and contrast: " + str(max_contrast))
    high_contrast_lines = []
    for i in range(len(lines_detected)):
        if (lines_detected[i][2] > max_contrast * 0.80):
            high_contrast_lines.append(lines_detected[i])

    for i in range(len(high_contrast_lines)):
        line = high_contrast_lines[i]
        if (((prev_line_count + merge_distance) < line[0]) and (current_counter >= 0)):
            return_lines_detected.append(high_contrast_lines[current_counter])
            current_counter = -100
            current_contrast = -100
        if ((line[2] > current_contrast)):
            current_counter = i
            current_contrast = line[2]
        prev_line_count = line[0]
    if (current_counter >= 0):
        return_lines_detected.append(high_contrast_lines[current_counter])

    return return_lines_detected


def pixel_diff(pix_1, pix_2):
    r_diff = (abs(int(pix_1[0]) - int(pix_2[0])))**2
    g_diff = (abs(int(pix_1[1]) - int(pix_2[1])))**2
    b_diff = (abs(int(pix_1[2]) - int(pix_2[2])))**2

    diff = r_diff + g_diff + b_diff
    return diff/255


def save_image_from_list(list_of_values,  file_out_name):
    image_height, image_width = len(list_of_values), len(list_of_values[0])
    rgbArray = np.zeros((image_height, image_width, 3), 'uint8')
    rgbArray[..., 0] = list_of_values
    rgbArray[..., 1] = list_of_values
    rgbArray[..., 2] = list_of_values

    print("rgb array:" + str(rgbArray.shape))
    img = Image.fromarray(rgbArray)
    print("Saving image: " + str(datetime.now().time()))
    img.save(file_out_name)
    print("Processed image: " + str(datetime.now().time()) + "\n\n\n")


def detect_lines(file, in_folder_name, out_folder_name):
    line_count = {}
    line_image = {}
    file_name_prefix = file.name[:-4]
    for horizontal_yn_flag in (True, False):
        file_name_suffix = 'hori' if horizontal_yn_flag == True else 'vert'

        dict_lines = {}
        dict_rationalized_lines = {}

        print("Processing: " + in_folder_name + file.name +
              " (" + file_name_suffix + " scan)\n")
        print("Start processing: " + str(datetime.now().time()))

        # rgb_matrix = imread(in_folder_name + file.name)
        rgb_matrix = imread(in_folder_name + file.name)

        # find size of the images
        image_height = len(rgb_matrix)
        image_width = len(rgb_matrix[0])
        image_channels = len(rgb_matrix[0][0])

        print("Shape: " + str(rgb_matrix.shape))

        # Create bitmap of matrix
        rgbArray = np.zeros((image_height, image_width, 3), 'uint8')

        print("Transforming RGB Matrix: " + str(datetime.now().time()))
        np_image_matrix = np.asarray(rgb_matrix)
        image_matrix = np_image_matrix.tolist()

        print("Finding contrast areas: " + str(datetime.now().time()))

        lines_matrix = image_with_lines(rgbArray,
                                        image_matrix, horizontal_yn_flag, dict_config)

        save_image_from_list(
            lines_matrix, rf"{out_folder_name}\{file_name_prefix}_lines_matrix_{file_name_suffix}.png")

        print("Computing contrast vector: " +
              str(datetime.now().time()))
        contrast_lines_vector = compute_contrast_vector(
            lines_matrix, horizontal_yn_flag, dict_config)

        # for j in range(len(contrast_lines_vector)) :
        ##            print(str(j) + ":" + str(contrast_lines_vector[j]))

        print("Finding lines: " + str(datetime.now().time()))
        lines_detected = detect_contrast_lines(
            lines_matrix, contrast_lines_vector, horizontal_yn_flag, dict_config)

        print("Rationalizing lines: " + str(datetime.now().time()))
        rationalized_lines_detected = rationalize_lines_detected(
            lines_detected)

        print("Painting lines: " + str(datetime.now().time()))
        image_with_contrast_lines = paint_lines(
            lines_matrix, rationalized_lines_detected, horizontal_yn_flag, dict_config)

        dict_lines[file.name] = lines_detected
        dict_rationalized_lines[file.name] = rationalized_lines_detected

        print("Creating RGB for output: " + str(datetime.now().time()))

        save_image_from_list(
            image_with_contrast_lines, rf"{out_folder_name}\{file_name_prefix}_{file_name_suffix}.png")

        for entry in dict_lines:
            print(entry)
        # print(dict_lines[entry])
            print(dict_rationalized_lines[entry])
        # file_log.close()
        line_count[horizontal_yn_flag] = len(
            dict_rationalized_lines[file.name])
        line_image[horizontal_yn_flag] = image_with_contrast_lines

    # Generate merged images
    merged_contrast_lines = line_image[False]
    hori_contrast_lines = line_image[True]
    for i in range(len(hori_contrast_lines)):
        for j in range(len(hori_contrast_lines[i])):
            if hori_contrast_lines[i][j] == 255:
                merged_contrast_lines[i][j] = 255

    save_image_from_list(
        merged_contrast_lines, rf"{out_folder_name}\{file_name_prefix}_merged.png")

    return line_count[True], line_count[False]


# str_file_log = "log\\log_txt.csv"
# file_log = open(str_file_log, "w")
str_file_config = "config_file.txt"
file_config = open(str_file_config, "r")
str_configs = file_config.read()
dict_config = json.loads(str_configs)

in_folder_name = dict_config.get("INPUT_FOLDER")
out_folder_name = dict_config.get("OUTPUT_FOLDER")

csv_in_file_name = None
error_folder = os.path.join(
    in_folder_name, 'error'+datetime.now().strftime("%Y%m%d-%H%M%S"))
os.mkdir(error_folder)
with os.scandir(in_folder_name) as entries:
    for file in entries:
        if(file.name.endswith(".csv")):
            csv_in_file_name = file.name
            with open(file, 'r') as csvfile_in:
                data_in = [row for row in csv.DictReader(csvfile_in)]
if(csv_in_file_name):
    report_file = out_folder_name+"report_"+csv_in_file_name
    header = ['file_name', 'Last_Updated_Time', 'Expected_column',
              'Extracted_column', 'Expected_row', 'Extracted_row', 'Status']
    out_files = glob.glob(out_folder_name + "*.csv")
    count = 0
    for out_file in out_files:
        if(out_file == report_file):
            count += 1
    if(count == 0):
        with open(report_file, 'w', newline='') as csvfile_out:
            writer = csv.DictWriter(csvfile_out, fieldnames=header)
            writer.writeheader()
    with os.scandir(in_folder_name) as entries:
        for file in entries:
            if(not file.name.endswith(".csv") and not file.name.find(".") == -1):
                actual_row, actual_col = detect_lines(
                    file, in_folder_name, out_folder_name)
                # actual_row, actual_col = '5', '7'
                tempfile = NamedTemporaryFile(
                    mode='w', delete=False, newline='')
                for row in data_in:
                    if row['file_name'] == file.name:
                        true_col = row['column']
                        true_row = row['row']
                        break
                found = False
                status = "Pass" if int(true_col) == actual_col and int(
                    true_row) == actual_row else "Fail"
                if(status == "Fail"):
                    shutil.copyfile(file, error_folder + '\\'+file.name)
                last_updated_time = str(datetime.now())
                with open(report_file, 'r') as csvfile_out, tempfile:
                    reader = csv.DictReader(csvfile_out, fieldnames=header)
                    writer = csv.DictWriter(tempfile, fieldnames=header)
                    for row in reader:
                        if row['file_name'] == file.name:
                            found = True
                            row['file_name'], row['Last_Updated_Time'], row['Expected_column'], row['Extracted_column'],  row[
                                'Expected_row'],  row['Extracted_row'], row['Status'] = file.name, last_updated_time, true_col, actual_col, true_row, actual_row, status
                        row = {'file_name': row['file_name'], 'Last_Updated_Time': row['Last_Updated_Time'], 'Expected_column': row['Expected_column'], 'Extracted_column':
                               row['Extracted_column'], 'Expected_row': row['Expected_row'], 'Extracted_row': row['Extracted_row'], 'Status': row['Status']}
                        writer.writerow(row)
                    if(found == False):
                        row = {'file_name': file.name, 'Last_Updated_Time': last_updated_time, 'Expected_column': true_col, 'Extracted_column':
                               actual_col, 'Expected_row': true_row, 'Extracted_row': actual_row, 'Status': status}
                        writer.writerow(row)
                shutil.move(tempfile.name, report_file)
    shutil.copyfile(in_folder_name+csv_in_file_name,
                    error_folder + '\\'+csv_in_file_name)
else:
    with os.scandir(in_folder_name) as entries:
        for file in entries:
            actual_row, actual_col = detect_lines(
                file, in_folder_name, out_folder_name)
