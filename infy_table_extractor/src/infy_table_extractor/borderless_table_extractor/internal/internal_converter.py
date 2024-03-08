# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import csv
import ntpath
import copy

from .extractor_util import ExtractorUtil

__logger = None


def read_file(input_file):
    elements = []
    cnt = 0
    with open(input_file, encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            element = []
            element.append(cnt)
            element.append(row[0])
            element.append(row[1])
            element.append(row[2])
            str_parts = extract_coordinates(row[3])
            for part in str_parts:
                element.append(int(float(part.strip())))
            cnt += 1
            elements.append(element)
    return elements


def extract_coordinates(str):
    str_2 = str[1:-1]
    str_parts = str_2.split(",")
    return str_parts

# find basic columns in table based on non-verlapping words in table


def get_basic_columns(words, threshold):
    table_columns = []
    column_num = 0

    # order words from left to right -> top to bottom
    words.sort(key=lambda word: word[4] * 100000 + word[5])
    current_column_left = -1
    current_column_right = -1

    for word in words:
        cell_left = word[4]
        cell_right = word[6]

        # check if cell overlaps with current column. consider threshold to avoid detection of word separation being considered as columns
        if (cell_left < current_column_right+threshold) and (cell_right > current_column_left-threshold):
            if (cell_left < current_column_left):
                current_column_left = cell_left
            if (cell_right > current_column_right):
                current_column_right = cell_right
        else:
            # new column detected, so add old column to table_columns list
            if (current_column_right != -1):
                column = []
                column.append(column_num)
                column.append(current_column_left)
                column.append(current_column_right)
                column_num += 1
                table_columns.append(column)

            current_column_left = cell_left
            current_column_right = cell_right
    # End: add old column to column_tables list
    column = []
    column.append(column_num)
    column.append(current_column_left)
    column.append(current_column_right)
    column_num += 1
    table_columns.append(column)

    return table_columns

# find basic rows in table based on non-verlapping words in table


def get_basic_rows(words):
    table_rows = []
    row_num = 0
    # order words from top to bottom then -> left to right
    words.sort(key=lambda word: word[5] * 100000 + word[4])
    current_row_top = -1
    current_row_bottom = -1
    current_row_mid = -1
    current_row_mid_pad = 0
    for word in words:
        cell_top = word[5]
        cell_bottom = word[7]

        # check if cell overlaps with current row wrt row middle. consider padding to address skewness and small words like "-"
        if (cell_top < current_row_mid + current_row_mid_pad) and (cell_bottom > current_row_mid - current_row_mid_pad):
            if (cell_top < current_row_top):
                current_row_top = cell_top
            if (cell_bottom > current_row_bottom):
                current_row_bottom = cell_bottom
            current_row_mid = (current_row_bottom + current_row_top) / 2
            current_row_mid_pad = (current_row_bottom - current_row_top) * 0.02
        else:
            # new row detected, so add old row to table_rows list
            if (current_row_bottom != -1):
                row = []
                row.append(row_num)
                row.append(current_row_top)
                row.append(current_row_bottom)
                row_num += 1
                table_rows.append(row)

            current_row_top = cell_top
            current_row_bottom = cell_bottom
            current_row_mid = (current_row_bottom + current_row_top) / 2
            current_row_mid_pad = (current_row_bottom - current_row_top) * 0.2
    # End: add old column to column_tables list
    row = []
    row.append(row_num)
    row.append(current_row_top)
    row.append(current_row_bottom)
    row_num += 1
    table_rows.append(row)

    return table_rows

# Find gaps between rows


def find_gaps(list):
    prev_end = list[0][1]
    for item in list:
        gap = item[1] - prev_end
        prev_end = item[2]
        item.append(gap)
    return list

# Find appropriate threshold for gaps between words such that columns can be detected


def analyze_word_gaps(words, row_list):
    threshold = 0
    gaps = []
    words.sort(key=lambda x: x[4])
    for row in row_list:
        prev_end = 0
        # for each row find gaps between words
        for word in words:
            if (word[5] >= row[1] and word[7] <= row[2]):
                if ((prev_end != 0) and (word[4] - prev_end) > 0):
                    gaps.append(word[4] - prev_end)
                prev_end = word[6]

    # find X percentile gap from the bottom of sorted list of gaps
    if (len(gaps) > 0):
        gaps.sort()
        tot = len(gaps)
        tot_30 = int(0.3 * tot)
        threshold = int(gaps[tot_30] * 1.6)
    else:
        threshold = 0
    return threshold


# Find appropriate threshold for gaps between rows such that closer rows can be detected
def analyze_row_gaps(row_list):
    threshold = 0
    gaps_list = []
    for row in row_list:
        if (row[3] != 0):
            # collect all row gaps in gaps_list except first row
            gap = []
            gap.append(row[3])
            gap.append(row[2] - row[1])
            gaps_list.append(gap)

    # find percentile from gaps list for row gap and corresponding height of row
    if (len(gaps_list) > 0):
        gaps_list.sort()
        tot = len(gaps_list)
        tot_30 = int(0.3 * tot)
        threshold = int(gaps_list[tot_30][0] * 3)
        height = gaps_list[tot_30][1]
    else:
        threshold = 0
        height = 0

    return threshold,  height

# create cells in table based on existing rows and word threshold


def formulate_basic_row_columns(words, table_rows, word_thresold):
    table = []
    row_num = 0
    column_num = 0

    words.sort(key=lambda x: x[4])
    for row in table_rows:
        cell_content = ""
        col_start = 0
        row_top = 0
        col_end = 0
        row_bottom = 0
        column_num = 0
        for word in words:
            # if word is in the row
            # word top >= row top and word bottom <= row bottom
            if (word[5] >= row[1] and word[7] <= row[2]):
                # if word is within word_threshold from prev word, then it should be considered to be within same cell and appended to cell content
                if ((col_end != 0) and (word[4] - col_end <= word_thresold)):
                    col_end = word[6]
                    cell_content = cell_content + " " + word[3]
                    if (row_top > word[5]):
                        row_top = word[5]
                    if (row_bottom > word[7]):
                        row_bottom = word[7]
                # if word is beyond word_threshold from prev word, then next cell is starting. so current cell should be added to table.
                elif ((col_end != 0) and (word[4] - col_end > word_thresold)):
                    table_cell = []
                    table_cell.append(row_num)
                    table_cell.append(column_num)
                    table_cell.append(cell_content)
                    table_cell.append(col_start)
                    table_cell.append(row_top)
                    table_cell.append(col_end)
                    table_cell.append(row_bottom)
                    table.append(table_cell)
                    column_num += 1
                    col_end = 0
                # Initialize for first word in cell
                if (col_end == 0):
                    col_start = word[4]
                    row_top = word[5]
                    col_end = word[6]
                    row_bottom = word[7]
                    cell_content = word[3]
        # End: Add last cell in row
        if (col_end != 0):
            table_cell = []
            table_cell.append(row_num)
            table_cell.append(column_num)
            table_cell.append(cell_content)
            table_cell.append(col_start)
            table_cell.append(row_top)
            table_cell.append(col_end)
            table_cell.append(row_bottom)
            table.append(table_cell)
        row_num += 1
    return table

# Add a column to table with # of columns in the table


def add_column_counts(table_rows, table, processing_msg=[]):
    processing_msg.append("Finding the row wise column count")
    new_table_rows = []
    row_num = 0
    for row in table_rows:
        column_count = 0
        # find count of rows for the row_num
        for cell in table:
            if (cell[0] == row_num):
                column_count += 1
        row.append(column_count)
        processing_msg.append(
            f"row num {row_num+1} and column count {column_count}")
        new_table_rows.append(row)
        row_num += 1
    return new_table_rows

# True if cells are overlapping horizontally - meaning they can potentially be merged. Vertical coordinates not considered


def is_cell_overlapping_by_column(cell_1, cell_2):
    overlapping = False
    if (cell_1[3] < cell_2[5] and cell_1[5] > cell_2[3]):
        overlapping = True
    return overlapping

# 1 if every cell in the row is vertically overlapping with max 1 cell in prev row;
# 0 - means at least one cell overlaps with multiple cells which makes it difficult for merging candidate


def update_row_overlapping_flag(table_rows, table, processing_msg=[]):
    processing_msg.append("Finding the row overlapping")
    new_table_rows = []
    row_num = 0
    for row in table_rows:
        overlap_flag = 0
        # cell_1: cell in current row
        for cell_1 in table:
            if (cell_1[0] == row_num):
                overlap_count = 0
                # cell_2: cell in previous row
                for cell_2 in table:
                    if (cell_2[0] == row_num-1):
                        if (is_cell_overlapping_by_column(cell_1, cell_2) == True):
                            overlap_count += 1
                if (overlap_count > 1):
                    overlap_flag = 1

        if overlap_flag == 1:
            processing_msg.append(
                f"Row number {row_num+1} - Every cell in the row is vertically overlapping with max 1 cell in prev row")
        else:
            processing_msg.append(
                f"Row number {row_num+1} - At least one cell overlaps with multiple cells which makes it difficult for merging candidate")

        row.append(overlap_flag)
        new_table_rows.append(row)
        row_num += 1
    return new_table_rows

# 1 if the current row should be considered short based on info compared with previous row


def update_row_short_row_flag(table_rows, processing_msg=[]):
    processing_msg.append("Finding the short row based on previous row.")
    new_table_rows = []
    row_num = 0
    short_row_flag = 0
    prev_short_row_flag = 0
    for row in table_rows:
        # initialize for first row
        if (row_num == 0):
            prev_column_count = row[4]
            short_row_flag = 0
            prev_short_row_flag = 0
        if (row_num > 0):
            # if prev row is NOT short, current row should have <= half of prev row's column count to be considered short
            if (prev_short_row_flag == 0):
                if (prev_column_count >= row[4] * 2):
                    short_row_flag = 1
                else:
                    short_row_flag = 0
            # if prev row is short, same or lower than prev row column count makes current row short
            elif (prev_short_row_flag == 1):
                if (prev_column_count >= row[4]):
                    short_row_flag = 1
                else:
                    short_row_flag = 0
            else:
                short_row_flag = 0
        if short_row_flag == 1:
            processing_msg.append(
                f"Row number {row_num+1} - is short row based on previouse row")
        row.append(short_row_flag)
        new_table_rows.append(row)
        prev_column_count = row[4]
        prev_short_row_flag = short_row_flag
        row_num += 1
    return new_table_rows

# 1 if gap between current row and previous is less than threshold ; else 0


def update_row_gap_flag(table_rows, gap_threshold, height_threshold, processing_msg=[]):
    processing_msg.append(
        "Finding and updating the row gap flag by comparing current and previous row")
    new_table_rows = []
    row_num = 0
    row_gap_for_merge_flag = 0
    for row in table_rows:
        if (row_num == 0):
            row_gap_for_merge_flag = 0
        if (row_num > 0):
            # Calculate gap for current row height and compare with row gap threshold
            gap_adjusted_for_height = (
                row[2] - row[1]) * row[3] / height_threshold
            if (gap_threshold >= gap_adjusted_for_height):
                row_gap_for_merge_flag = 1
                processing_msg.append(
                    f"Current row {row_num+1} and previous row gap {gap_adjusted_for_height} is less than threshold {gap_threshold}")
            else:
                row_gap_for_merge_flag = 0
                processing_msg.append(
                    f"Current row {row_num+1} and previous row gap {gap_adjusted_for_height} is greater than threshold {gap_threshold}")

        row.append(row_gap_for_merge_flag)
        new_table_rows.append(row)
        row_num += 1
    return new_table_rows

# 1 for rows that have higher count than prev row or prev master rows; else 0


def update_row_master_flag(table_rows, processing_msg=[]):
    processing_msg.append("Finding and updating the row master flag")
    new_table_rows = []
    row_master_flag = 0
    master_column_count = 0
    prev_column_count = 0
    row_num = 0
    for row in table_rows:
        current_column_count = row[4]
        # Row is conidered master if its count is higher that prev row or prev master row
        if (current_column_count > prev_column_count or current_column_count >= master_column_count):
            row_master_flag = 1
            master_column_count = current_column_count
        else:
            row_master_flag = 0

        if row_master_flag == 1:
            processing_msg.append(f"Row {row_num+1} is master")

        row.append(row_master_flag)
        new_table_rows.append(row)
        prev_column_count = current_column_count
        row_num += 1

    return new_table_rows


# skip header rows and merge specified count of rows into single row by appending cells horizontally
def post_process_table(table, dict_config):
    header_rows_count = int(dict_config.get("HEADER_ROWS_COUNT"))
    merge_rows_count = int(dict_config.get("MERGE_DETAIL_ROWS_COUNT"))

    row_num = 0
    column_num = 0
    prev_cell_row_num = 0
    prev_cell_column_num = 0
    for cell in table:
        cell_row_num = cell[0]
        cell_column_num = cell[1]

        # when row changes, reset row_num to prev row for non-header rows that meet merging criteria
        if (prev_cell_row_num != cell_row_num):
            row_num += 1
            if (cell_row_num >= header_rows_count):
                # if row to be merged, reduce row_num by 1
                if ((cell_row_num - header_rows_count) % merge_rows_count != 0):
                    row_num -= 1
                else:
                    column_num = 0

        # override information in existing cell with new row num and column num
        cell[0] = row_num
        cell[1] = column_num

        # set values for next cell
        column_num += 1
        prev_cell_row_num = cell_row_num
        prev_cell_column_num = cell_column_num

    return table

# skip header rows and merge row into prev row by appending cells horizontally


def merge_short_rows(table, dict_config):
    header_rows_count = int(dict_config.get("HEADER_ROWS_COUNT"))
    merge_column_threshold = int(dict_config.get("MERGE_COLUMN_THRESHOLD"))
    footer_start_text = dict_config.get("FOOTER_START_TEXT")
    row_num = 0
    column_num = 0
    prev_cell_row_num = 0
    prev_cell_column_num = 0
    for cell in table:
        cell_row_num = cell[0]
        cell_column_num = cell[1]

        # when row num changes, reset row_num to prev row for non-header rows
        if (prev_cell_row_num != cell_row_num):
            row_num += 1

            if (cell_row_num >= header_rows_count):
                # count # of columns in the row of current cell
                column_count = 0
                for cell_2 in table:
                    if (cell_2[0] == cell_row_num):
                        column_count += 1
                # if row to be merged, reduce row_num by 1
                if (column_count < merge_column_threshold and cell[2][0:len(footer_start_text)] != footer_start_text):
                    row_num -= 1
                else:
                    column_num = 0

        # override information in existing cell with new row num and column num
        cell[0] = row_num
        cell[1] = column_num

        # set values for next cell
        column_num += 1
        prev_cell_row_num = cell_row_num
        prev_cell_column_num = cell_column_num

    return table

# replace header in table with columns specified in config file


def replace_table_header(table, dict_config):
    header_rows_count = int(dict_config.get("HEADER_ROWS_COUNT"))
    dict_column_details = dict_config.get("COLUMNS")
    column_count = dict_column_details.get("COLUMN_COUNT")

    new_table = []

    # add row with columns from config file
    for column_num in range(column_count):
        new_cell = []
        new_cell.append(0)
        new_cell.append(column_num)
        column_label = "COLUMN_DETAILS_" + str(column_num)
        dict_column = dict_column_details.get(column_label)
        new_cell.append(dict_column.get("LABEL"))
        new_table.append(new_cell)

    # add non header rows from the table after initial row with column headers
    for cell in table:
        if (cell[0] >= header_rows_count):
            cell[0] = cell[0] - header_rows_count + 1
            new_table.append(cell)
    return new_table


# remove blank rows from the table such that row num are in proper sequence
def remove_blank_rows(table):
    # find max row number in table
    row_count = 0
    for cell in table:
        if (row_count < cell[0]):
            row_count = cell[0]

    new_table = []
    new_row_num = 0
    for row_num in range(row_count+1):
        row_exists_in_table = False
        # if cell found with current row number, update new_row_num; new_row_num counter is incremented only when at least one cell for a row is detected
        for cell in table:
            if (row_num == cell[0]):
                row_exists_in_table = True
                cell[0] = new_row_num
                new_table.append(cell)
        if (row_exists_in_table == True):
            new_row_num += 1
    return new_table

# formulate table by breaking rows into column as specified in table_columns list


def discover_columns(table, table_columns):
    column_count = len(table_columns)

    # find max row num in table
    row_count = 0
    for cell in table:
        if (row_count < cell[0]):
            row_count = cell[0]

    new_table = []
    for row_num in range(row_count+1):
        # check if row by rown num exists in table
        row_exists_in_table = False
        for cell in table:
            if (row_num == cell[0]):
                row_exists_in_table = True
        # if row exists, create column for every column in table_columns
        if (row_exists_in_table == True):
            for column_num in range(column_count):

                new_cell = []
                cell_content = ""
                # for each cell within the column boundary, collect content and add new cell to new_table
                for cell in table:
                    column_left = table_columns[column_num][1]
                    column_right = table_columns[column_num][2]
                    if (row_num == cell[0] and cell[3] < column_right and cell[5] > column_left):
                        cell_content = cell_content + cell[2]
                new_cell.append(row_num)
                new_cell.append(column_num)
                new_cell.append(cell_content)
                new_table.append(new_cell)
    return new_table


# formulate table by breaking rows into column as specified in config file
def formulate_columns(table, dict_config):
    dict_column_details = dict_config.get("COLUMNS")
    column_count = dict_column_details.get("COLUMN_COUNT")

    # find max row num in table
    row_count = 0
    for cell in table:
        if (row_count < cell[0]):
            row_count = cell[0]

    new_table = []
    for row_num in range(row_count+1):
        # check if row by rown num exists in table
        row_exists_in_table = False
        for cell in table:
            if (row_num == cell[0]):
                row_exists_in_table = True
        # if row exists, create column for every column specified in config file
        if (row_exists_in_table == True):
            for column_num in range(column_count):

                new_cell = []
                column_label = "COLUMN_DETAILS_" + str(column_num)
                dict_column_pos = dict_column_details.get(column_label)
                # for each cell within the column boundary, collect content and add new cell to new_table
                cell_content = ""
                for cell in table:
                    column_left = dict_column_pos.get("LEFT")
                    column_right = dict_column_pos.get("RIGHT")
                    if (row_num == cell[0] and cell[3] < column_right and cell[5] > column_left):
                        cell_content = cell_content + cell[2]
                new_cell.append(row_num)
                new_cell.append(column_num)
                new_cell.append(cell_content)
                new_table.append(new_cell)
    return new_table

# Update final flag if row is candidate for merging with previous row


def update_row_merge_flag(table_rows, dict_config, processing_msg=[]):
    new_table_rows = []
    row_num = 0
    for row in table_rows:
        row_merge_flag = 0
        # Merge flag = 1 based on Overlap flag=0, Short row flag = 1, Row gap flag = 1, Master flag= 0
        if (row[5] == 0 and row[6] == 1 and row[7] == 1 and row[8] == 0):
            row_merge_flag = 1

        # Merge flag = 1 based on column count specified in config file
        if (bool(dict_config) and dict_config.get("MERGE_MULTI_LINE_BY_COL_COUNT") == "Y" and dict_config.get("MERGE_MULTI_LINE_COL_COUNT") == str(row[4])):
            row_merge_flag = 1

        if row_merge_flag == 1:
            processing_msg.append(
                f"Updating the flag to merge Row {row_num+1} with prev row")
        row.append(row_merge_flag)
        new_table_rows.append(row)
        row_num += 1
    return new_table_rows

# Merge overlapping cells across tables based on merge flag for the row in table_rows


def merge_rows_in_table(table_rows, table):
    master_row_num = 0
    for row in table_rows:
        # if merge flag = 0 for the row, indicate that the cell will merge with itself
        if (row[9] == 0):
            for cell in table:
                if (cell[0] == row[0]):
                    cell.append(cell[0])
                    cell.append(cell[1])
        else:
            # if merge flag is not zero, identify cell to be merged for each cell in the row
            for cell_1 in table:
                if (cell_1[0] == row[0]):
                    merge_with_row = 0
                    merge_with_column = 0
                    merge_found_flag = False
                    # find cell in master row num that overlaps with current cell
                    for cell_2 in table:
                        if (cell_2[0] == master_row_num and is_cell_overlapping_by_column(cell_1, cell_2) == True):
                            merge_with_row = cell_2[7]
                            merge_with_column = cell_2[8]
                            merge_found_flag = True
                    if (merge_found_flag == False):
                        merge_with_row = cell_1[0]
                        merge_with_column = cell_1[1]
                    cell_1.append(merge_with_row)
                    cell_1.append(merge_with_column)
        master_row_num = row[0]
    return table


def merge_cells_in_table(table):
    new_table = []
    for cell_1 in table:
        txt_cell_content = ""
        for cell_2 in table:
            # row num == merge row num and col num == merge col num
            if (cell_1[0] == cell_2[7] and cell_1[1] == cell_2[8]):
                txt_cell_content = txt_cell_content + cell_2[2] + " "
        if (len(txt_cell_content) != 0):
            new_cell = []
            new_cell.append(cell_1[0])
            new_cell.append(cell_1[1])
            new_cell.append(txt_cell_content)
            new_cell.append(cell_1[3])
            new_cell.append(cell_1[4])
            new_cell.append(cell_1[5])
            new_cell.append(cell_1[6])
            new_table.append(new_cell)
    return new_table


def sort_cols(table, table_rows_with_gaps_col_cnt):
    table_rows_with_gaps_col_cnt.sort(key=lambda x: x[4], reverse=True)
    max_col_row_num = table_rows_with_gaps_col_cnt[0][0]
    new_table_rows = []
    for row in table:
        new_row = list(row)
        if new_row[0] != max_col_row_num:
            # current row col left <= max cal row col left then set max row col to current
            max_col_rows = [row for row in table if row[0] == max_col_row_num]
            for idx, max_row_col in enumerate(max_col_rows):
                if new_row[3] <= max_row_col[5]:
                    new_row[1] = max_row_col[1]
                    break
        new_table_rows.append(new_row)
    return new_table_rows


def create_table_html(file_out, table):
    file_out.write("<!DOCTYPE html>")
    file_out.write("<head> <title>HTML Tables</title> </head>")
    file_out.write("<body>")
    prev_row_num = -1
    prev_column_num = -1

    file_out.write("<table border='1'>\n")
    for cell in table:
        row_num = cell[0]
        column_num = cell[1]
        if (prev_row_num != row_num):
            if (prev_row_num != -1):
                file_out.write("</td>\n")
                file_out.write("</tr>\n")
            file_out.write("<tr>\n")
            prev_column_num = -1
        if (prev_column_num != column_num):
            if (prev_column_num != -1):
                file_out.write("</td>\n")
            # create empty cell
            for i in range(prev_column_num+1, column_num):
                file_out.write("<td></td>\n")
            file_out.write("<td>\n")
        file_out.write(cell[2] + " ")
        prev_row_num = row_num
        prev_column_num = column_num

    file_out.write("</td>\n")
    file_out.write("</tr>\n")
    file_out.write("</table>\n")
    file_out.write("</body>\n")
    file_out.write("</html>\n")


def convert_coordinates_to_html_table(logger, csv_file_list, output_dir, dict_config, config_param_dict, processing_msg=[]):
    """
    Parameters
    ----------
    logger : logging
    csv_file_list : list
        list of csv files contains words and its coordinates.
    dict_config : dictionary
        Basic Configuration to filter out table from image to html
    output_dir : string
            All .html output files will be generated to output_dir
    """
    if(logger == None):
        raise Exception('logger object is None')
    table_response = []
    try:
        __logger = logger
        for csv_file in csv_file_list:
            elements = read_file(csv_file)

            # Processing of rows
            table_rows = get_basic_rows(elements)
            processing_msg.append(f"Found Row counts are - {len(table_rows)}")

            table_rows_with_gaps = find_gaps(table_rows)

            word_gap_threshold = analyze_word_gaps(
                elements, table_rows_with_gaps)
            processing_msg.append(
                f"Found word's gap threshold is {word_gap_threshold}")

            row_gap_threshold, row_height_threshold = analyze_row_gaps(
                table_rows_with_gaps)
            table = formulate_basic_row_columns(
                elements, table_rows_with_gaps, word_gap_threshold)
            processing_msg.append(
                f"Found Row's gap threshold {row_gap_threshold} and height threshold {row_height_threshold} ")
            # 4
            table_rows_with_gaps_col_cnt = add_column_counts(
                table_rows_with_gaps, table, processing_msg)
            # 5
            table_rows_with_overlap_flag = update_row_overlapping_flag(
                table_rows_with_gaps_col_cnt, table, processing_msg)
            # 6
            table_rows_with_short_row_flag = update_row_short_row_flag(
                table_rows_with_overlap_flag, processing_msg)
            # 7
            table_rows_with_gap_flag = update_row_gap_flag(
                table_rows_with_short_row_flag, row_gap_threshold, row_height_threshold, processing_msg)
            # 8
            table_rows_with_master_flag = update_row_master_flag(
                table_rows_with_gap_flag, processing_msg)
            # 9
            table_rows_with_merge_flag = update_row_merge_flag(
                table_rows_with_master_flag, dict_config, processing_msg)
            table_merged = merge_rows_in_table(
                table_rows_with_merge_flag, table)

            table_merged_cells = merge_cells_in_table(table_merged)
            table_merged_cells_without_blank = remove_blank_rows(
                table_merged_cells)

            table_sorted_cells = sort_cols(
                table_merged_cells_without_blank, table_rows_with_gaps_col_cnt)

            table_processed = table_sorted_cells
            if(bool(dict_config)):
                if (dict_config.get("MERGE_ROWS") == "Y"):
                    __logger.info('MERGE_ROWS=Y')
                    processing_msg.append("MERGE_ROWS flag enabled")
                    table_processed = post_process_table(
                        table_processed, dict_config)

                if (dict_config.get("MERGE_SHORT_ROWS") == "Y"):
                    __logger.info('MERGE_SHORT_ROWS=Y')
                    processing_msg.append("MERGE_SHORT_ROWS flag enabled")
                    table_processed = merge_short_rows(
                        table_processed, dict_config)

                if (dict_config.get("REPLACE_HEADER") == "Y"):
                    __logger.info('REPLACE_HEADER=Y')
                    processing_msg.append("REPLACE_HEADER flag enabled")
                    table_processed = replace_table_header(
                        table_processed, dict_config)

                if (dict_config.get("FORMULATE_COLUMNS") == "Y"):
                    __logger.info('FORMULATE_COLUMNS=Y')
                    processing_msg.append(
                        "FORMULATE_COLUMNS - Breaking row to column flag enabled")
                    table_processed = formulate_columns(
                        table_processed, dict_config)

                if (dict_config.get("DISCOVER_COLUMNS") == "Y"):
                    __logger.info('DISCOVER_COLUMNS=Y')
                    processing_msg.append("DISCOVER_COLUMNS flag enabled")
                    table_columns = get_basic_columns(elements, 30)
                    table_processed = discover_columns(
                        table_processed, table_columns)
            # TODO for this flow, customcell logic need to revisited
            # table_processed = ExtractorUtil.extract_custom_cells(
            #     table_processed, config_param_dict)
            processing_msg.append(
                f"extracted the custom cells as in {config_param_dict}")
            if output_dir:
                file_out_name = output_dir + '/' + ntpath.basename(
                    csv_file).replace('_word_bbox.csv', '.html')
                with open(file_out_name, 'w') as filehandle:
                    create_table_html(filehandle, table_processed)
                    __logger.info(file_out_name + ' generated.')
                    processing_msg.append(
                        f"HTML file generated to {file_out_name}")

            table_response = _create_dict_from_tbl(table_processed)

        return table_response
    except Exception as e:
        raise e


def _create_dict_from_tbl(table_processed):
    tbl_dict_base = {}
    p_row = 0
    tbl_dict_list = []
    tbl_dict = {}
    for tbl_val in table_processed:
        c_row = tbl_val[0]
        if c_row == 0:
            tbl_dict_base[tbl_val[2].strip()] = ""
        else:
            if p_row != c_row:
                if p_row != 0:
                    tbl_dict_list.append(copy.copy(tbl_dict))
                temp_key_list = list(tbl_dict_base.items())
                tbl_dict = copy.copy(tbl_dict_base)
            try:
                tbl_dict[temp_key_list[tbl_val[1]][0]] = tbl_val[2].strip()
            except:
                # TODO:add warning msg
                pass
            p_row = c_row

    return tbl_dict_list
