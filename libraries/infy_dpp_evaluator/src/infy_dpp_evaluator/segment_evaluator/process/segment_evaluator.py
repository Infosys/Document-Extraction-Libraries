"""Module to evaluate the extracted data from the segment detector and structure recognizer modules."""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


from csv import DictReader
import os
import json
import shutil
import itertools
from typing import List
import pandas as pd
from bs4 import BeautifulSoup
from shapely.geometry import Polygon
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_evaluator.common.file_util import FileUtil
from infy_dpp_evaluator.segment_evaluator.process.segment_evaluator_extension import SegmentEvaluatorExtension
from infy_dpp_evaluator.segment_evaluator.service.grits import grits_from_html
PROCESSEOR_CONTEXT_DATA_NAME = "segment_evaluator"


class SegmentEvaluator(infy_dpp_sdk.interface.IProcessor):
    """Class to evaluate TD and TSR extracted data."""

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__app_config = self.get_app_config()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        def __add_html_tags(text):
            if '<html>' not in text and '</html>' not in text:
                if '<body>' not in text and '</body>' not in text:
                    text = "<body>" + text + "</body>"
                text = "<html>" + text + "</html>"
            return text

        processor_response_data = ProcessorResponseData()
        segment_evaluator_config_data = config_data.get('SegmentEvaluator', {})
        output_root_path = segment_evaluator_config_data.get(
            'output_root_path')+f"D-{FileUtil.get_uuid()}"

        evaluation = segment_evaluator_config_data.get('evaluation', {})
        detector = evaluation.get("detector")
        structure_recognizer = evaluation.get(
            "structure_recognizer").get('enabled')
        grits_enabled = evaluation.get(
            "structure_recognizer").get('grits_enabled')

        # output_root_path = segment_evaluator_config_data.get('output_root_path')
        container_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        doc_truth_data_path = context_data['request_creator']['docs_truth_data_path']
        result_data_path = context_data['request_creator']['result_data_path']
        prev_ext_file_path = context_data['request_creator']['prev_docs_ext_data_path']
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {}
        CONFIG_DICT = {
            'MIN_OVERLAP_PCT_FULL_MATCH': 80,
            'MIN_OVERLAP_PCT_PARTIAL_MATCH': 70
        }
        config_data = config_data.get('SegmentEvaluator', {})
        config_data.get('output_root_path')
        output_folder_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{output_root_path}/metrics'
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        output_file_path = f'{output_folder_path}/extracted_data_metrics.json'
        output_model_stats_file_path = f'{output_folder_path}/extracted_data_model_stats.json'
        # copying meta data to records

        doc_truth_data_paths_list = []
        if doc_truth_data_path:
            doc_truth_data_path_files = self.__read_files(doc_truth_data_path)
            doc_truth_data_path_list = [
                doc_truth_data_file for doc_truth_data_file
                in doc_truth_data_path_files if doc_truth_data_file.lower().endswith(('.csv', '.xlsx'))]
            for truth_data_path in doc_truth_data_path_list:
                doc_truth_data_paths_list.append(
                    __get_temp_file_path(truth_data_path))

        if result_data_path:
            result_data_paths_list = []
            result_data_paths = self.__read_files(result_data_path)
            result_data_path_list = [
                result_data_file for result_data_file
                in result_data_paths if result_data_file.lower().endswith(('.json'))]
            for result_data_paths in result_data_path_list:
                result_data_paths_list.append(
                    __get_temp_file_path(result_data_paths))

        result_data_folder = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{result_data_path}'
        # if previous extracted data present then adding current result folder
        if prev_ext_file_path:
            prev_ext_files_paths_list = []
            prev_ext_file_path = self.__read_files(prev_ext_file_path)
            prev_ext_files_path_list = [
                prev_ext_file for prev_ext_file
                in prev_ext_file_path if prev_ext_file.lower().endswith(('.json'))]
            for prev_ext_files in prev_ext_files_path_list:
                prev_ext_files_paths_list.append(
                    __get_temp_file_path(prev_ext_files))
            for prev_ext_file in prev_ext_files_paths_list:
                server_file_dir = os.path.dirname(prev_ext_file.replace('\\', '/').replace('//', '/').replace(
                    self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
                local_dir = os.path.dirname(prev_ext_file)
                self._upload_data(f'{local_dir}', f'{server_file_dir}')
                shutil.copy(prev_ext_file, result_data_folder)

        all_model_records = []
        dataset_list = []
        # module_result_files = os.listdir(result_data_folder)
        module_result_files = []
        if (context_data.get("segment_structure_recognizer")):
            tsr_aggregated_result_file_name = os.path.basename(context_data.get("segment_structure_recognizer").get(
                "tsr_aggregate_data_path"))
            module_result_files.append(
                tsr_aggregated_result_file_name)  # tsr_aggregated_file

        if (context_data.get("segment_detector")):
            yolox_aggregated_result_file_name = os.path.basename(context_data.get(
                "segment_detector").get("yolox_aggregate_data_path"))
            module_result_files.append(
                yolox_aggregated_result_file_name)  # yolox_aggregated_file

        if detector and structure_recognizer:
            # Merge the JSON files from the two modules
            module_result_files = self.__merge_result_files(
                module_result_files, result_data_folder)
            self.__logger.info("Merged result files")

        if detector:
            self.__update_config_dict(
                module_result_files, result_data_folder, CONFIG_DICT)
        seg_evaluator_extension = SegmentEvaluatorExtension(self.__logger)

        for model_result_file in module_result_files:
            file_read_path = result_data_folder + "/" + model_result_file
            with open(file_read_path, encoding='utf-8-sig') as file:
                data = json.load(file)
                # adding metadata to records
                meta_data = data['metadata']
                dataset_list.append(meta_data['dataset_name_with_version'])
                records_key_list = [k for k, v in data['records'][0].items()]
                if detector:
                    meta_data['model_name'] = f"{data['metadata']['model_identifier']}_{data['metadata']['model_run_version']}"
                    # filter meta data
                    updated_metadata = {k: v for k, v in meta_data.items(
                    ) if 'model_' in k and 'model_identifier'not in k and 'model_run_version' not in k}
                    # check if duplicate key present in records and metadata
                    meta_data_key_list = [
                        k for k, v in updated_metadata.items()]
                    for key in meta_data_key_list:
                        if key in records_key_list:
                            raise Exception(
                                f"This metadata key - '{key}' is present in records . Cannot override")
                    for i in data['records']:
                        i.update(updated_metadata)
            # all_model_records.append({'metadata': meta_data})
            all_model_records += data['records']
            # all_model_records.append({'records': data['records']})

            dataset_list = list(set(dataset_list))
            if len(dataset_list) > 1:
                print(dataset_list)
                raise ValueError(
                    'More than one dataset found which can give incorrect results! Please load results files for one dataset only!')

            all_model_records_data = [
                x for x in all_model_records if x['bbox']]
            all_model_records_data.sort(key=lambda x: (x['image_subpath']))
        for docs_truth_data_path in doc_truth_data_paths_list:
            truth_data_list = None
            with open(docs_truth_data_path, encoding='utf-8-sig') as file:
                dict_reader = DictReader(file)
                truth_data_list = list(dict_reader)
        if detector:
            calculated_accuracy = self.__calculate_record_accuracy(
                truth_data_list, all_model_records_data)
            all_model_records, all_model_stats = self.__add_unmatched_records(
                truth_data_list, calculated_accuracy)
            FileUtil.save_as_json_file_if_different(
                output_model_stats_file_path, all_model_stats)
        if structure_recognizer:
            truth_image_subpath_list = list(
                set([x['image_subpath'] for x in truth_data_list]))
            last_image_name = None
            table_num = None
            for truth_data in truth_data_list:
                if last_image_name == truth_data['image_subpath']:
                    table_num += 1
                else:
                    table_num = 65  # Ascii value for A
                truth_data['truth_table_name'] = "table_" + chr(
                    table_num) + "_" + truth_data['x1'] + "_" + truth_data['y1'] + "_" + truth_data['x2'] + "_" + truth_data['y2']
                last_image_name = truth_data['image_subpath']
            # For each image loop
            for truth_image_subpath in truth_image_subpath_list:
                _truth_data_list = [
                    x for x in truth_data_list if x['image_subpath'] == truth_image_subpath]
                all_model_image_records = [
                    x for x in all_model_records if x['image_subpath'] == truth_image_subpath]
                for record in all_model_image_records:
                    for truth_data in _truth_data_list:
                        truth_bbox = [truth_data['x1'], truth_data['y1'],
                                      truth_data['x2'], truth_data['y2']]
                        truth_bbox = [float(x) for x in truth_bbox]
                        record_bbox = record['bbox']
                        # truth_table_name = truth_data['truth_table_name']
                        # truth_class_prefix_kv_dict = {
                        #     k: v for k, v in truth_data.items() if k.startswith('class_')}
                        bboxes_match = self.__compare_bboxes(
                            truth_bbox, record_bbox, 500)
                        if bboxes_match:
                            td_rows_str = truth_data['rows']
                            td_cols_str = truth_data['columns']
                            td_rows_str = truth_data.get('rows', 0)
                            td_cols_str = truth_data.get('columns', 0)
                            td_rows = int(td_rows_str)
                            td_cols = int(td_cols_str)
                            ext_rows = record.get('no_of_rows', 0)
                            ext_cols = record.get('no_of_columns', 0)
                            self.__logger.debug(
                                "Extracted rows: %s and columns: %s for %s", ext_rows, ext_cols, record_bbox)
                            row_accuracy = self.calc_accuracy(
                                ext_rows, td_rows)
                            col_accuracy = self.calc_accuracy(
                                ext_cols, td_cols)
                            record['row_accuracy'] = row_accuracy
                            record['col_accuracy'] = col_accuracy
                            # grits metric
                            if grits_enabled:
                                if truth_data.get('html_file_subpath'):
                                    truth_html_filepath = doc_truth_data_path + \
                                        "/" + \
                                        truth_data.get('html_file_subpath')
                                    try:
                                        truth_html_filepath = __get_temp_file_path(
                                            truth_html_filepath)
                                        with open(truth_html_filepath, 'r', encoding='utf-8') as file:
                                            truth_html_content = file.read()

                                        truth_html_content = __add_html_tags(
                                            truth_html_content)
                                        predicted_html_content = record.get(
                                            'table_html_data', '')
                                        if predicted_html_content:
                                            predicted_html_content = __add_html_tags(
                                                predicted_html_content)
                                            grits_metric = grits_from_html(
                                                str(BeautifulSoup(
                                                    truth_html_content, 'html.parser')),
                                                str(BeautifulSoup(
                                                    predicted_html_content, 'html.parser'))
                                            )
                                            # record['grits_metric'] = grits_metric
                                            for key, value in grits_metric.items():
                                                record[key] = value
                                    except Exception:
                                        self.__logger.error(
                                            f"Error while reading truth html file or No such file or directory {truth_data.get('html_file_subpath')}")
                            break

        FileUtil.save_as_json_file_if_different(
            output_file_path, all_model_records)

        server_file_dir = os.path.dirname(output_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(output_file_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        metric_data_source_path = output_file_path.replace(
            container_path+"/", '')
        metric_data_path_list = []
        metric_data_path_list.insert(0, metric_data_source_path)
        all_model_records_df = pd.DataFrame(all_model_records)
        columns_with_class = [x for x in list(
            all_model_records_df.columns) if x.startswith('class')]
        ordered_col_value_list = []
        for col_name in columns_with_class:
            col_values = list(all_model_records_df[col_name].dropna().unique())
            ordered_col_value_list.append(col_values)
        # Only 2 columns supported currently
        col_value_combination_list = []
        if len(ordered_col_value_list) == 2:
            col_value_combination_list = list(itertools.product(
                ordered_col_value_list[0], ordered_col_value_list[1]))
        elif len(ordered_col_value_list) == 1:
            col_value_combination_list = [
                (x,) for x in ordered_col_value_list[0]]  # list of 1D tuple
        # col_value_combination_list, len(col_value_combination_list)

        if detector:
            filter_dict = {}
            for idx_comb, col_value_combination in enumerate(col_value_combination_list):
                # print(col_value_combination, type(col_value_combination), len(col_value_combination))
                for col_name in columns_with_class:
                    filter_dict[col_name] = []
                for idx, col_value in enumerate(col_value_combination):
                    col_name = columns_with_class[idx]
                    filter_dict[col_name].append(col_value)
                # print(filter_dict)
                filtered_data_list = seg_evaluator_extension.apply_filter(
                    all_model_records, filter_dict, columns_with_class)
                # print(len(filtered_data_list))
                avg_matrix_list = seg_evaluator_extension.calc_average_overlap_pct(
                    filtered_data_list, CONFIG_DICT)
                conf_matrix_list = seg_evaluator_extension.calc_confusion_matrix(
                    filtered_data_list, CONFIG_DICT)
                data = {
                    'metadata': {
                        'filter': filter_dict
                    },
                    'records_conf_matrix': conf_matrix_list,
                    'records_overlap_pct': avg_matrix_list
                }
                output_file_path_list = fr"{output_file_path}_filter_{idx_comb + 1}.json"
                FileUtil.save_as_json_file_if_different(
                    output_file_path_list, data)
                server_file_dir = os.path.dirname(output_file_path_list.replace('\\', '/').replace('//', '/').replace(
                    self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
                local_dir = os.path.dirname(output_file_path_list)
                self._upload_data(f'{local_dir}', f'{server_file_dir}')

                metric_data_path = output_file_path_list.replace(
                    container_path+"/", '')
                metric_data_path_list.append(metric_data_path)
                # metric_data_path_list.insert(0, metric_data_source_path)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME]['segment_evaluator_data_path'] = metric_data_path_list
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

    def __calculate_record_accuracy(self, truth_data_list, all_model_records) -> list:
        def calculate_bbox_overlap(for_bbox, from_bbox):
            for_bbox_area = (for_bbox[2]) * (for_bbox[3])
            from_bbox_area = (from_bbox[2])*(from_bbox[3])
            # print(for_bbox_area, from_bbox_area)
            p_x1, p_x2, p_y1, p_y2 = for_bbox[0], for_bbox[0] + \
                for_bbox[2], for_bbox[1], for_bbox[1]+for_bbox[3]
            o_x1, o_x2, o_y1, o_y2 = from_bbox[0], from_bbox[0] + \
                from_bbox[2], from_bbox[1], from_bbox[1]+from_bbox[3]
            p_points = [(p_x2, p_y1), (p_x2, p_y2), (p_x1, p_y2), (p_x1, p_y1)]
            o_points = [(o_x2, o_y1), (o_x2, o_y2), (o_x1, o_y2), (o_x1, o_y1)]
            # print(p_points, o_points)
            polygon = Polygon(p_points)
            other_polygon = Polygon(o_points)
            intersection = polygon.intersection(other_polygon)
            union = polygon.union(other_polygon)
            # print(intersection.area)
            # return round((max(intersection.area/for_bbox_area, intersection.area/from_bbox_area)*100), 2)
            return round((intersection.area/union.area)*100, 2)
        # Get list of images to be used as group by
        truth_image_subpath_list = list(
            set([x['image_subpath'] for x in truth_data_list]))
        last_image_name = None
        table_num = None
        for truth_data in truth_data_list:
            if last_image_name == truth_data['image_subpath']:
                table_num += 1
            else:
                table_num = 65  # Ascii value for A
            truth_data['truth_table_name'] = "table_" + chr(
                table_num) + "_" + truth_data['x1'] + "_" + truth_data['y1'] + "_" + truth_data['x2'] + "_" + truth_data['y2']
            last_image_name = truth_data['image_subpath']
        # For each image loop
        for truth_image_subpath in truth_image_subpath_list:
            _truth_data_list = [
                x for x in truth_data_list if x['image_subpath'] == truth_image_subpath]
            for truth_data in _truth_data_list:
                truth_table_name = truth_data['truth_table_name']
                truth_bbox = [truth_data['x1'], truth_data['y1'],
                              truth_data['x2'], truth_data['y2']]
                truth_bbox = [float(x) for x in truth_bbox]
                truth_class_prefix_kv_dict = {
                    k: v for k, v in truth_data.items() if k.startswith('class_')}
                # print(truth_class_prefix_kv_dict)
                all_model_image_records = [
                    x for x in all_model_records if x['image_subpath'] == truth_image_subpath]
                # print(json.dumps(truth_data, indent=4))
                # print(json.dumps(all_model_image_records, indent=4))
                all_model_names = list(
                    set([x['model_name'] for x in all_model_image_records]))
                # print(all_model_names)
                for model_name in all_model_names:
                    image_model_records = [x for x in all_model_image_records if x['model_name'] == model_name
                                           and not x.get('truth_source', None)]
                    # print(json.dumps(image_model_records, indent=4))
                    max_overlap_pct = -1
                    max_overlap_idx = -1
                    for idx, image_model_record in enumerate(image_model_records):
                        bbox = image_model_record['bbox']
                        # print(truth_bbox, 'vs', bbox)
                        if bbox:
                            _bbox = [
                                bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1]]
                            _truth_bbox = [
                                truth_bbox[0], truth_bbox[1], truth_bbox[2]-truth_bbox[0], truth_bbox[3]-truth_bbox[1]]
                            score = calculate_bbox_overlap(
                                _truth_bbox, _bbox)
                            score = score if score > 0 else -1
                            if score > max_overlap_pct:
                                max_overlap_pct = score
                                max_overlap_idx = idx
                    # print('max_overlap_idx =', max_overlap_idx, 'max_overlap_pct =' , max_overlap_pct )
                    for idx, _ in enumerate(image_model_records):
                        if idx == max_overlap_idx:
                            image_model_records[idx]['truth_overlap_pct'] = max_overlap_pct
                            image_model_records[idx]['truth_table_name'] = truth_table_name
                            image_model_records[idx]['truth_source'] = 'match-found'
                            image_model_records[idx].update(
                                truth_class_prefix_kv_dict)

            # print(json.dumps(all_model_records, indent=4))
            # At this stage, 1 image with all tables from truth data completed for all models
            # For records in extracted data where no match was found, update with default values
            all_model_image_records = [
                x for x in all_model_records if x['image_subpath'] == truth_image_subpath]
            for idx, all_model_image_record in enumerate(all_model_image_records):
                if not all_model_image_record.get('truth_source', None):
                    all_model_image_record['truth_overlap_pct'] = -1
                    all_model_image_record['truth_table_name'] = None
                    all_model_image_record['truth_source'] = 'match-not-found'

        return all_model_records

    def __add_unmatched_records(self, truth_data_list, all_model_records) -> list:
        all_model_stats = []
        all_model_names = list(set([x['model_name']
                               for x in all_model_records]))
        for model_name in all_model_names:
            model_stats = {
                'model_name': model_name,
                'extracted_count': -1,
                'truth_data_count': -1,
                'truth_data_match_count': -1,
                'truth_data_unmatched_count': -1,
                'records_modified_count': -1,
                'records_added_count': -1,
                'final_count': -1
            }

            single_model_records = [
                x for x in all_model_records if x['model_name'] == model_name]
            model_stats['extracted_count'] = len(single_model_records)

            truth_table_names = [x['truth_table_name']
                                 for x in truth_data_list]
            model_stats['truth_data_count'] = len(truth_table_names)
            # print(json.dumps(truth_table_names, indent=4))

            matched_table_names = [x.get('truth_table_name', None) for x in single_model_records if x.get(
                'truth_table_name', None) is not None]
            model_stats['truth_data_match_count'] = len(matched_table_names)
            # print(json.dumps(matched_table_names, indent=4))

            unmatched_table_names = list(
                set(truth_table_names) - set(matched_table_names))
            unmatched_table_names = sorted(unmatched_table_names)
            model_stats['truth_data_unmatched_count'] = len(
                unmatched_table_names)
            # print(json.dumps(unmatched_table_names, indent=4))

            records_modified_count, records_added_count = 0, 0
            for unmatched_table_name in unmatched_table_names:
                truth_record = [
                    x for x in truth_data_list if x['truth_table_name'] == unmatched_table_name][0]
                truth_class_prefix_kv_dict = {
                    k: v for k, v in truth_record.items() if k.startswith('class_')}
                existing_records = [x for x in all_model_records if x['image_subpath'] == truth_record['image_subpath']
                                    and x['model_name'] == model_name
                                    and x.get('truth_table_name', None) is None]
                existing_records.sort(
                    key=lambda x: (str(x['truth_table_name'])))
                if existing_records:
                    existing_record = existing_records[0]
                    existing_record['truth_table_name'] = unmatched_table_name
                    existing_record['truth_overlap_pct'] = -1
                    existing_record['truth_source'] = existing_record['truth_source'] + \
                        ";best-guess-applied"
                    existing_record.update(truth_class_prefix_kv_dict)
                    records_modified_count += 1
                else:
                    all_model_records.append({
                        'image_subpath': truth_record['image_subpath'],
                        'object_type': 'Table',
                        'bbox_format': 'X1,Y1,X2,Y2',
                        'bbox': [],
                        'td_confidence_pct': -1.0,
                        'model_run_id': None,
                        'model_name': model_name,
                        'truth_overlap_pct': -1,
                        'truth_table_name': unmatched_table_name,
                        'truth_source': 'entity-not-extracted',
                        **truth_class_prefix_kv_dict,
                    })
                    records_added_count += 1
            model_stats['records_modified_count'] = records_modified_count
            model_stats['records_added_count'] = records_added_count
            model_stats['final_count'] = len(
                [x for x in all_model_records if x['model_name'] == model_name])
            all_model_stats.append(model_stats)

        return all_model_records, all_model_stats

    def __update_config_dict(self, model_result_files, extracted_data_folder, CONFIG_DICT):
        model_sort_order = []
        model_name_to_image_bbox_name_suffix_map = {}
        prev_fie_dataset_name = ''
        unique_model_name_list = []

        for model_result_file in model_result_files:
            file_read_path = extracted_data_folder + "/" + model_result_file
            with open(file_read_path, encoding='utf-8-sig') as file:
                data = json.load(file)
                # adding metadata to records
                meta_data = data['metadata']
                model_identifier = meta_data['model_identifier']
                model_run_version = meta_data['model_run_version']
                model_run_id = meta_data['model_run_id']
                if len(prev_fie_dataset_name) == 0:
                    prev_fie_dataset_name = meta_data['dataset_name_with_version']
                else:
                    if prev_fie_dataset_name != meta_data['dataset_name_with_version']:
                        raise Exception(
                            f"Dataset name and version is not matching for {model_identifier}")
                unique_model_name = f'{model_identifier}_{model_run_version}'
                if unique_model_name not in unique_model_name_list:
                    unique_model_name_list.append(unique_model_name)
                else:
                    raise Exception(
                        f'{unique_model_name} is duplicate . please check')
                model_sort_order.append(unique_model_name)
                model_name_to_image_bbox_name_suffix_map[
                    unique_model_name] = f'{model_identifier}/{model_run_id}'

        CONFIG_DICT.update({'MODEL_SORT_ORDER': model_sort_order})
        CONFIG_DICT.update(
            {'MODEL_NAME_TO_BBOX_IMAGE_NAME_SUFFIX_MAP': model_name_to_image_bbox_name_suffix_map})

    def __read_files(self, from_files_folder_path) -> List[str]:
        found_files = self.__file_sys_handler.list_files(
            from_files_folder_path)
        if len(found_files) > 0:
            self.__logger.info(
                "Found %d files in %s", len(found_files), from_files_folder_path)
        else:
            self.__logger.info(
                "No files found in %s, stopping pipeline execution", from_files_folder_path)
        return found_files

    def calc_accuracy(self, ext_x, td_x):
        """calculate accuracy"""
        x_accuracy = 0
        if ext_x is not None and td_x is not None:
            diff_x = ext_x - td_x
            if diff_x < 0:
                diff_x = abs(diff_x)
            x_error = diff_x / td_x
            if x_error > 1:
                x_error = 1
            x_accuracy = 1 - x_error
        return round(x_accuracy * 100, 2)

    def __merge_result_files(self, module_result_files, result_data_folder, variation=500):
        """Merge the JSON files from the two modules"""

        updated_module_result_files = []
        file_1 = module_result_files[0]  # tsr_aggregated_file
        file_2 = module_result_files[1]  # yolox_aggregated_file

        full_file_1_path = result_data_folder + '/' + file_1
        full_file_2_path = result_data_folder + '/' + file_2

        with open(full_file_1_path, 'r', encoding='utf-8-sig') as file:
            file_1_data = json.load(file)

        with open(full_file_2_path, 'r', encoding='utf-8-sig') as file:
            file_2_data = json.load(file)
        combined_metadata = {
            **file_1_data['metadata'], **file_2_data['metadata']}

        self.__logger.debug("file_1_data: %s", file_1_data)
        self.__logger.debug("file_2_data: %s", file_2_data)
        # Create a dictionary to map bbox to records for quick lookup
        file_1_records_dict = {
            tuple(record['bbox']): record for record in file_1_data['records']}
        file_2_records_dict = {
            tuple(record['bbox']): record for record in file_2_data['records']}

        # Combine records based on bbox
        combined_records = []
        for bbox, file_1_record in file_1_records_dict.items():
            x1_1 = int(bbox[0])
            y1_1 = int(bbox[1])
            for bbox_2, file_2_record in file_2_records_dict.items():
                x1_2 = int(bbox_2[0])
                y1_2 = int(bbox_2[1])
                # if x1_1 == x1_2 and y1_1 == y1_2:
                if abs(x1_1 - x1_2) <= variation and abs(y1_1 - y1_2) <= variation:
                    combined_record = self.__merge_records(
                        file_1_record, file_2_record)
                    combined_records.append(combined_record)
                    break  # Assuming one match per record
        combined_data = {
            'metadata': combined_metadata,
            'records': combined_records
        }
        self.__logger.debug("combined_data: %s", combined_data)
        combined_file_path = result_data_folder + '/combined_result.json'

        with open(combined_file_path, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=4)

        updated_module_result_files.append('combined_result.json')
        return updated_module_result_files

    def __merge_records(self, record1, record2):
        """Merge two records, giving precedence to non-null values."""
        merged_record = {}
        all_keys = set(record1.keys()).union(set(record2.keys()))

        for key in all_keys:
            value1 = record1.get(key)
            value2 = record2.get(key)

            if value1 is not None and value2 is not None:
                merged_record[key] = value1 if value1 is not None else value2
            elif value1 is not None:
                merged_record[key] = value1
            else:
                merged_record[key] = value2

        return merged_record

    def __compare_bboxes_old(self, truth_bbox, record_bbox):
        """Compare if each value in the respective lists matches"""
        return all(t == r for t, r in zip(truth_bbox, record_bbox))

    def __compare_bboxes(self, truth_bbox, record_bbox, variation=20):
        """Compare if each value in the respective lists matches within a variation"""
        return all(abs(t - r) <= variation for t, r in zip(truth_bbox, record_bbox))
