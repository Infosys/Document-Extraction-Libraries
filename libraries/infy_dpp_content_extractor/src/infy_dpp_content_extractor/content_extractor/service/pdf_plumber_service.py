# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import pdfplumber
from infy_dpp_content_extractor.common.file_util import FileUtil
import traceback


class PdfPlumberService:
    def __init__(self, logger,app_config, file_sys_handler, text_provider_dict):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler
        self.__text_provider_dict = text_provider_dict
        self.__extract_hyperlinks = self.__text_provider_dict.get(
            'properties', {}).get('extract_hyperlink', False)
        self.__table_settings =  self.__text_provider_dict.get(
            'properties', {}).get('table_settings', {})
        self.__debug = self.__text_provider_dict.get(
            'properties', {}).get('debug', {})

    def get_tables_content(self, from_files_full_path, out_file_full_path) -> list:
        try:
            with pdfplumber.open(from_files_full_path) as pdf:
                all_pages = []
                work_path = out_file_full_path.replace(self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"],'')
                abs_work_path = self.__file_sys_handler.get_abs_path(work_path).replace('filefile://','')

                for page in pdf.pages:
                    page_tables = []
                    table_objects = page.find_tables()
                    
                    # Use table settings if provided
                    if self.__table_settings is not None and len(self.__table_settings) > 0:
                        tables = page.extract_tables(table_settings=self.__table_settings)
                    else:
                        tables = page.extract_tables()
                        
                    # Save an image for each table on the page
                    if self.__debug.get('enabled', False):
                        debug_path = work_path + '/' + self.__debug.get('output_dir_path','')
                        debug_fullpath = abs_work_path + '/' + self.__debug.get('output_dir_path','')
                        self.__file_sys_handler.create_folders(debug_path, create_parents=True)
        
                        for table_index, table_object in enumerate(table_objects):
                            table_image = page.to_image().debug_tablefinder()
                            table_image.save(debug_fullpath + f"page_{page.page_number}_table_{table_index + 1}.png")
            
                    table_number = 1

                    page_words = page.extract_words()
                    hyperlinks_list = self._get_hyperlinks_list(page)

                    for table, table_object in zip(tables, table_objects):
                        header = table[0]
                        table_data = [dict(zip(header, row))
                                      for row in table[1:]]
                        header_bbox, data_bbox, data_html, header_bbox_value, data_bbox_value = [], [], [], [], []
                        min_y1 = None

                        # determine the min_y1 to find header row
                        for cell in table_object.cells:
                            cell_bbox = cell
                            cell_y1 = cell_bbox[1]
                            if min_y1 is None or cell_y1 < min_y1:
                                min_y1 = cell_y1

                        # based in the min y1 value find fill header_bbox and data_bbox
                        for cell in table_object.cells:
                            cell_bbox = cell
                            cell_y1 = cell_bbox[1]
                            cell_info = {
                                'bbox': cell_bbox
                            }

                            cell_words = [
                                word for word in page_words if self._get_words_in_cell(word, cell_bbox)]
                            cell_info_value = cell_info.copy()
                            cell_info_value['value'] = cell_words

                            if cell_y1 == min_y1:
                                header_bbox.append(cell_info)
                                header_bbox_value.append(cell_info_value)
                            else:
                                data_bbox.append(cell_info)
                                data_bbox_value.append(cell_info_value)

                            # Add col_idx and row_idx to header and data cells
                            for col_idx, cell_info in enumerate(header_bbox):
                                cell_info['col_idx'] = col_idx
                                cell_info['row_idx'] = 0
                            num_columns = len(header)
                            column_cells = {col_idx: []
                                            for col_idx in range(num_columns)}
                            for cell_info in data_bbox:
                                try:
                                    for col_idx in range(num_columns):
                                        if cell_info['bbox'][0] == header_bbox[col_idx]['bbox'][0]:
                                            column_cells[col_idx].append(
                                                cell_info)
                                            break
                                except IndexError:
                                    continue
                            for col_idx, cells in column_cells.items():
                                try:
                                    for row_idx, cell_info in enumerate(cells):
                                        cell_info['col_idx'] = col_idx
                                        cell_info['row_idx'] = row_idx + 1
                                except IndexError:
                                    continue

                        # Create data_html object if extract_hyperlinks is enabled
                        if self.__extract_hyperlinks:
                            data_html = self._create_data_html(
                                table_data, header_bbox_value, data_bbox_value, hyperlinks_list)

                        page_tables.append({
                            "table_id": f"p{page.page_number}_tb{table_number}",
                            "bbox": table_object.bbox,
                            "data": table_data,
                            "header_bbox": header_bbox,
                            "data_bbox": data_bbox,
                            "data_html": data_html
                        })
                        table_number += 1

                    page_dict = {
                        "page_number": page.page_number,
                        "page_width": page.bbox[2],
                        "page_height": page.bbox[3],
                        "tables": page_tables
                    }

                    all_pages.append(page_dict)

            # Define the output file path for the entire PDF
            output_file_path = os.path.join(
                out_file_full_path, f"{os.path.basename(from_files_full_path)}_pdfplumber.json")

            FileUtil.save_to_json(output_file_path, all_pages)

            return output_file_path
        except Exception as e:
            trace = traceback.format_exc()
            self.__logger.error(f"Error in extracting tables from pdf: {e}")
            return []

    def _get_words_in_cell(self, word, cell_bbox, tolerance=5):
        word_bbox = (word['x0'], word['top'], word['x1'], word['bottom'])
        return (word_bbox[0] >= cell_bbox[0] - tolerance and word_bbox[2] <= cell_bbox[2] + tolerance and
                word_bbox[1] >= cell_bbox[1] - tolerance and word_bbox[3] <= cell_bbox[3] + tolerance)

    def _get_hyperlinks_list(self, page):
        hyperlinks_info = []
        for hyperlink in page.hyperlinks:
            link_bbox = (hyperlink['x0'], hyperlink['top'],
                         hyperlink['x1'], hyperlink['bottom'])
            hyperlinks_info.append({
                'uri': hyperlink['uri'],
                'bbox': link_bbox
            })
        return hyperlinks_info

    def _create_data_html(self, table_data, header_bbox, data_bbox, hyperlinks_info):
        data_html = []
        processed_word_bboxes = []
        for row in table_data:
            row_html = {}
            for key, value in row.items():
                value = value.replace('\n', ' ') if value else value

                # Process key for hyperlinks
                key = self._process_hyperlinks(key, header_bbox, hyperlinks_info, processed_word_bboxes, is_header=True)

                # Process value for hyperlinks
                value = self._process_hyperlinks(value, data_bbox, hyperlinks_info, processed_word_bboxes, is_header=False)

                row_html[key] = value
            data_html.append(row_html)
        return data_html

    def _process_hyperlinks(self, text, bbox, hyperlinks_info, processed_word_bboxes, is_header):
        if not text:
            return text

        words = text.split()
        processed_words = []
        combined_words = []
        current_hyperlink = None

        reorganized_bbox = self._reorganize_bbox(bbox)
        for word in words:
            word_bbox = None
            for cell_info in reorganized_bbox:
                if cell_info['value']:
                    for cell_word in cell_info['value']:
                        if cell_word['text'] == word:
                            word_bbox = [cell_word['x0'], cell_word['top'], cell_word['x1'], cell_word['bottom']]
                            if not is_header and word_bbox and (word, tuple(word_bbox)) in processed_word_bboxes:
                                word_bbox = None
                            else:
                                break
                if word_bbox:
                    break

            if word_bbox:
                hyperlink_found = False
                for hyperlink in hyperlinks_info:
                    if self._check_bbox_intersection(word_bbox, hyperlink['bbox']):
                        if current_hyperlink == hyperlink['uri']:
                            combined_words.append(word)
                        else:
                            if current_hyperlink:
                                processed_words.append(f'<a href="{current_hyperlink}">{" ".join(combined_words)}</a>')
                            combined_words = [word]
                            current_hyperlink = hyperlink['uri']
                        hyperlink_found = True
                        cell_info['value'].remove(cell_word) 
                        break
                if not hyperlink_found:
                    if current_hyperlink:
                        processed_words.append(f'<a href="{current_hyperlink}">{" ".join(combined_words)}</a>')
                        combined_words = []
                        current_hyperlink = None
                    processed_words.append(word)
            else:
                if current_hyperlink:
                    processed_words.append(f'<a href="{current_hyperlink}">{" ".join(combined_words)}</a>')
                    combined_words = []
                    current_hyperlink = None
                processed_words.append(word)
               
            if not is_header and word_bbox:    
                processed_word_bboxes.append((word, tuple(word_bbox)))

        if current_hyperlink:
            processed_words.append(f'<a href="{current_hyperlink}">{" ".join(combined_words)}</a>')

        return ' '.join(processed_words)

    def _reorganize_bbox(self, bbox):
        columns = {}
        for cell_info in bbox:
            x0 = cell_info['bbox'][0]
            if x0 not in columns:
                columns[x0] = []
            columns[x0].append(cell_info)

        # Sort the columns
        sorted_x0_values = sorted(columns.keys())

        # Reorganize bbox list
        reorganized_bbox = []
        if columns:
            max_length = max(len(columns[x0]) for x0 in sorted_x0_values)
            for i in range(max_length):
                for x0 in sorted_x0_values:
                    if i < len(columns[x0]):
                        reorganized_bbox.append(columns[x0][i])

        return reorganized_bbox
        
    def _check_bbox_intersection(self, word_bbox, hyperlink_bbox, threshold=0.6):
        x_left = max(word_bbox[0], hyperlink_bbox[0])
        y_top = max(word_bbox[1], hyperlink_bbox[1])
        x_right = min(word_bbox[2], hyperlink_bbox[2])
        y_bottom = min(word_bbox[3], hyperlink_bbox[3])

        if x_right < x_left or y_bottom < y_top:
            return False

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        word_bbox_area = (word_bbox[2] - word_bbox[0]) * \
            (word_bbox[3] - word_bbox[1])

        # Check if the intersection area ratio meets the threshold
        return (intersection_area / word_bbox_area) >= threshold
