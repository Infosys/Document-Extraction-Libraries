# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import csv
from typing import List
import pandas as pd
import numpy as np
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_evaluator.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "segment_reporter"


class SegmentReporter(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        self.__logger.debug('Segment Report Generation Started')
        processor_response_data = ProcessorResponseData()
        config_data = config_data.get('SegmentReporter', {})
        metrics_json_path = context_data['segment_evaluator']['segment_evaluator_data_path'][0]

        doc_truth_data_path = context_data['request_creator']['docs_truth_data_path']
        container_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        output_root_path = container_path + config_data.get('output_root_path')
        raw_report_file_name = config_data.get(
            'file_type').get('raw_report_file_name')
        aggregated_report_file_name = config_data.get(
            'file_type').get('aggregated_report_file_name')
        min_true_positive_overlap_pct = config_data.get(
            'metrics_threshold').get('min_true_positive_overlap_pct')
        min_true_positive_row_column_accuracy_pct = config_data.get(
            'metrics_threshold').get('min_true_positive_row_column_accuracy_pct')

        doc_truth_data_path = self.__read_files(doc_truth_data_path)

        truth_data_csv_path_list = [
            doc_truth_data_file for doc_truth_data_file
            in doc_truth_data_path if doc_truth_data_file.lower().endswith(('.csv', '.xlsx'))]

        metrics_json_full_path = __get_temp_file_path(metrics_json_path)
        truth_data_csv_full_path = __get_temp_file_path(
            truth_data_csv_path_list[0])
        report_csv_file_path, report_json_file_path, aggregated_report_csv_file_path, aggregated_report_json_file_path = self.__consolidate_data(
            truth_data_csv_full_path, metrics_json_full_path, output_root_path, raw_report_file_name, aggregated_report_file_name, min_true_positive_overlap_pct, min_true_positive_row_column_accuracy_pct)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "raw_segment_report_csv_file_path": report_csv_file_path,
            "raw_segment_report_json_file_path": report_json_file_path,
            "aggregated_segment_report_csv_file_path": aggregated_report_csv_file_path,
            "aggregated_segment_report_json_file_path": aggregated_report_json_file_path
        }

        self.__logger.debug('Segment Report Generation Completed')
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data
        return processor_response_data

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

    def __consolidate_data(self, csv_file_path, json_file_path, output_root_path, raw_report_file_name, aggregated_report_file_name, min_true_positive_overlap_pct, min_true_positive_row_column_accuracy_pct):
        # Read CSV file
        with open(csv_file_path, encoding='utf-8-sig') as file:
            dict_reader = csv.DictReader(file)
            truth_data_list = list(dict_reader)

        # Read JSON file
        with open(json_file_path, 'r') as file:
            metrics_data_list = json.load(file)

        updated_truth_data_list = []
        filtered_metrics_data_list = []
        for metrics_data in metrics_data_list:
            # Filter out records where "truth_source" key exists and its value is "match-not-found"
            # filtered_metrics_data = [record for record in metrics_data if record.get(
            #     'truth_source') != 'match-not-found']
            if metrics_data.get('truth_source') != 'match-not-found':
                metrics_data.pop('table_html_data', None)
                filtered_metrics_data_list.append(metrics_data)

        for data in truth_data_list:
            updated_truth_data = {}
            for k, v in data.items():
                if k != 'image_subpath' and k != 'image_path':
                    updated_truth_data[f"truth_{k}"] = v
                else:
                    updated_truth_data[k] = v

            for metrics_data in filtered_metrics_data_list:
                if len(metrics_data['bbox']) == 0:
                    for k, v in metrics_data.items():
                        if k not in data and not k.startswith('grits'):
                            updated_truth_data[f"td_{k}"] = v
                        else:
                            updated_truth_data[k] = v
                    filtered_metrics_data_list.remove(metrics_data)
                    break
                else:
                    bboxes_match = self.__compare_bboxes(data, metrics_data)
                    if data['image_subpath'] == metrics_data['image_subpath'] and bboxes_match:
                        for k, v in metrics_data.items():
                            if k not in data and not k.startswith('grits'):
                                updated_truth_data[f"td_{k}"] = v
                            else:
                                updated_truth_data[k] = v
                        filtered_metrics_data_list.remove(metrics_data)
                        break
            updated_truth_data_list.append(updated_truth_data)

        # Extract aggregated metrics
        aggregated_metrics = self.__extract_aggregated_metrics(
            updated_truth_data_list, min_true_positive_overlap_pct, min_true_positive_row_column_accuracy_pct)
        # save the updated truth data to a new CSV file and json file
        found_folder = None
        for item in os.listdir(output_root_path):
            item_path = os.path.join(output_root_path, item)
            if os.path.isdir(item_path):
                found_folder = item_path
                break
        # Create 'report' folder inside the found folder
        report_folder_path = os.path.join(found_folder, 'report')
        os.makedirs(report_folder_path, exist_ok=True)
        # Create CSV file inside the 'report' folder
        # report_csv_file_path = os.path.join(
        #     report_folder_path, 'segment_report.csv')
        report_csv_file_path = os.path.join(
            report_folder_path, (raw_report_file_name + '.csv'))

        updated_truth_data_item_with_max_keys = max(updated_truth_data_list,
                                                    key=lambda item: len(item.keys()))
        with open(report_csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(
                csv_file, fieldnames=updated_truth_data_item_with_max_keys.keys())
            writer.writeheader()
            writer.writerows(updated_truth_data_list)

        aggregated_report_csv_file_path = os.path.join(
            report_folder_path, (aggregated_report_file_name + '.csv'))
        aggregated_metrics.to_csv(aggregated_report_csv_file_path, index=False)
        # Create JSON file inside the 'report' folder
        report_json_file_path = os.path.join(
            report_folder_path, (raw_report_file_name + '.json'))
        FileUtil.save_to_json(
            report_json_file_path, updated_truth_data_list)

        aggregated_report_json_file_path = os.path.join(
            report_folder_path, (aggregated_report_file_name + '.json'))
        aggregated_metrics.to_json(
            aggregated_report_json_file_path, orient='records', indent=4)
        server_file_dir = os.path.dirname(report_json_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(report_json_file_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        report_json_file_path = report_json_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        report_csv_file_path = report_csv_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        aggregated_report_json_file_path = aggregated_report_json_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        aggregated_report_csv_file_path = aggregated_report_csv_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        return report_csv_file_path, report_json_file_path, aggregated_report_csv_file_path, aggregated_report_json_file_path

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

    def __compare_bboxes(self, truth_data, metrics_data):
        bboxes_match = False
        # Check if the necessary keys exist and their values are not null or empty
        if ('y1' in truth_data and truth_data['y1'] is not None and truth_data['y1'] != '' and
            'bbox' in metrics_data and len(metrics_data['bbox']) > 1 and
                metrics_data['bbox'][1] is not None):
            if abs(float(truth_data['y1']) - metrics_data['bbox'][1]) <= 80:
                bboxes_match = True
        return bboxes_match

    def __extract_aggregated_metrics(self, segment_report_list, min_true_positive_overlap_pct, min_true_positive_row_column_accuracy_pct):
        def get_valid_table_count(series):
            return series[(series.notnull()) & (series != -1)].count()

        def get_td_true_positive_count(series):
            return series[(series.notnull()) & (series != -1) & (series >= min_true_positive_overlap_pct)].count()

        def get_tsr_true_positive_count(series):
            return series[(series.notnull()) & (series != -1) & (series >= min_true_positive_row_column_accuracy_pct)].count()

        df = pd.DataFrame(segment_report_list)

        if "td_row_accuracy" not in df.columns:
            # Perform the aggregation
            grouped_df = df.groupby(['truth_class_border_type']).agg({
                'image_subpath': 'count',
                'td_truth_overlap_pct': ['sum', get_valid_table_count, get_td_true_positive_count]
            }).reset_index()

            # Rename the columns
            grouped_df.columns = [
                'Class Border Type',
                'Actual Tables Count',
                'Sum TD Overlap %',
                'TD Tables Detected',
                'TD True Positive'
            ]

            grouped_df['Mean TD Overlap %'] = grouped_df['Sum TD Overlap %'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TD Incorrect Detection'] = grouped_df['TD Tables Detected'] - \
                grouped_df['TD True Positive']
            grouped_df['No Data'] = grouped_df['Actual Tables Count'] - \
                grouped_df['TD Tables Detected']
            grouped_df['TD Precision'] = np.where(
                grouped_df['TD Tables Detected'] == 0,
                0,
                grouped_df['TD True Positive'] /
                grouped_df['TD Tables Detected']
            )
            grouped_df['TD Recall'] = grouped_df['TD True Positive'] / \
                grouped_df['Actual Tables Count']
            grouped_df = grouped_df.drop(columns=['Sum TD Overlap %'])
        elif "td_truth_overlap_pct" not in df.columns:
            grouped_df = df.groupby(['truth_class_border_type']).agg({
                'image_subpath': 'count',
                'td_row_accuracy': ['sum', get_valid_table_count, get_tsr_true_positive_count],
                'td_col_accuracy': ['sum', get_valid_table_count, get_tsr_true_positive_count]
            }).reset_index()

            # Rename the columns
            grouped_df.columns = [
                'Class Border Type',
                'Actual Tables Count',
                'Sum TSR Row Accuracy',
                'TSR Rows Recognized',
                'TSR Rows True Positive',
                'Sum TSR Column Accuracy',
                'TSR Columns Recognized',
                'TSR Columns True Positive'
            ]

            grouped_df['Mean TSR Row Accuracy'] = grouped_df['Sum TSR Row Accuracy'] / \
                grouped_df['Actual Tables Count']
            grouped_df['Mean TSR Column Accuracy'] = grouped_df['Sum TSR Column Accuracy'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TSR Incorrect Rows Recognized'] = grouped_df['TSR Rows Recognized'] - \
                grouped_df['TSR Rows True Positive']
            grouped_df['TSR Incorrect Columns Recognized'] = grouped_df['TSR Columns Recognized'] - \
                grouped_df['TSR Columns True Positive']
            grouped_df['No Data'] = grouped_df['Actual Tables Count'] - \
                grouped_df['TSR Rows Recognized']
            grouped_df['TSR Row Precision'] = np.where(
                grouped_df['TSR Rows Recognized'] == 0,
                0,
                grouped_df['TSR Rows True Positive'] /
                grouped_df['TSR Rows Recognized']
            )
            grouped_df['TSR Column Precision'] = np.where(
                grouped_df['TSR Columns Recognized'] == 0,
                0,
                grouped_df['TSR Columns True Positive'] /
                grouped_df['TSR Columns Recognized']
            )
            grouped_df['TSR Rows Recall'] = grouped_df['TSR Rows True Positive'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TSR Columns Recall'] = grouped_df['TSR Columns True Positive'] / \
                grouped_df['Actual Tables Count']
            # Remove the sum entries from the final grouped_df
            grouped_df = grouped_df.drop(
                columns=['Sum TSR Row Accuracy', 'Sum TSR Column Accuracy'])
        else:
            # Perform the aggregation
            grouped_df = df.groupby(['truth_class_border_type']).agg({
                'image_subpath': 'count',
                'td_truth_overlap_pct': ['sum', get_valid_table_count, get_td_true_positive_count],
                'td_row_accuracy': ['sum', get_valid_table_count, get_tsr_true_positive_count],
                'td_col_accuracy': ['sum', get_valid_table_count, get_tsr_true_positive_count]
            }).reset_index()

            # Rename the columns
            grouped_df.columns = [
                'Class Border Type',
                'Actual Tables Count',
                'Sum TD Overlap %',
                'TD Tables Detected',
                'TD True Positive',
                'Sum TSR Row Accuracy',
                'TSR Rows Recognized',
                'TSR Rows True Positive',
                'Sum TSR Column Accuracy',
                'TSR Columns Recognized',
                'TSR Columns True Positive'
            ]

            grouped_df['Mean TD Overlap %'] = grouped_df['Sum TD Overlap %'] / \
                grouped_df['Actual Tables Count']
            grouped_df['Mean TSR Row Accuracy'] = grouped_df['Sum TSR Row Accuracy'] / \
                grouped_df['Actual Tables Count']
            grouped_df['Mean TSR Column Accuracy'] = grouped_df['Sum TSR Column Accuracy'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TD Incorrect Detection'] = grouped_df['TD Tables Detected'] - \
                grouped_df['TD True Positive']
            grouped_df['TSR Incorrect Rows Recognized'] = grouped_df['TSR Rows Recognized'] - \
                grouped_df['TSR Rows True Positive']
            grouped_df['TSR Incorrect Columns Recognized'] = grouped_df['TSR Columns Recognized'] - \
                grouped_df['TSR Columns True Positive']
            grouped_df['No Data'] = grouped_df['Actual Tables Count'] - \
                grouped_df['TD Tables Detected']
            grouped_df['TD Precision'] = np.where(
                grouped_df['TD Tables Detected'] == 0,
                0,
                grouped_df['TD True Positive'] /
                grouped_df['TD Tables Detected']
            )
            grouped_df['TSR Row Precision'] = np.where(
                grouped_df['TSR Rows Recognized'] == 0,
                0,
                grouped_df['TSR Rows True Positive'] /
                grouped_df['TSR Rows Recognized']
            )
            grouped_df['TSR Column Precision'] = np.where(
                grouped_df['TSR Columns Recognized'] == 0,
                0,
                grouped_df['TSR Columns True Positive'] /
                grouped_df['TSR Columns Recognized']
            )
            grouped_df['TD Recall'] = grouped_df['TD True Positive'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TSR Rows Recall'] = grouped_df['TSR Rows True Positive'] / \
                grouped_df['Actual Tables Count']
            grouped_df['TSR Columns Recall'] = grouped_df['TSR Columns True Positive'] / \
                grouped_df['Actual Tables Count']
            # Remove the sum entries from the final grouped_df
            grouped_df = grouped_df.drop(
                columns=['Sum TD Overlap %', 'Sum TSR Row Accuracy', 'Sum TSR Column Accuracy'])

        if 'grits_top' in df.columns:
            # Perform the aggregation for grits
            grits_grouped_df = df.groupby(['truth_class_border_type']).agg({
                'image_subpath': 'count',
                'grits_top': 'sum',
                'grits_precision_top': 'sum',
                'grits_recall_top': 'sum',
                'grits_top_upper_bound': 'sum',
                'grits_con': 'sum',
                'grits_precision_con': 'sum',
                'grits_recall_con': 'sum',
                'grits_con_upper_bound': 'sum'
            }).reset_index()

            grouped_df['Mean grits Top'] = grits_grouped_df['grits_top'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_precision_top'] = grits_grouped_df['grits_precision_top'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_recall_top'] = grits_grouped_df['grits_recall_top'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_top_upper_bound'] = grits_grouped_df['grits_top_upper_bound'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_con'] = grits_grouped_df['grits_con'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_precision_con'] = grits_grouped_df['grits_precision_con'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_recall_con'] = grits_grouped_df['grits_recall_con'] / \
                grits_grouped_df['image_subpath']
            grouped_df['Mean grits_con_upper_bound'] = grits_grouped_df['grits_con_upper_bound'] / \
                grits_grouped_df['image_subpath']

        return grouped_df
