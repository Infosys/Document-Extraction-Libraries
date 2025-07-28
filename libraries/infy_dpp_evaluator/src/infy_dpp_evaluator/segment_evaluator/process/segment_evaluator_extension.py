# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


class SegmentEvaluatorExtension():
    def __init__(self, logger):
        self.__logger = logger

    def apply_filter(self, all_model_records: list, filter_dict: dict, columns_with_class):
        filtered_data_list = []
        for data in all_model_records:
            cnf = set()
            for i in range(len(columns_with_class)):
                col_name = columns_with_class[i]
                col_values = filter_dict[col_name]
                if col_values and col_name in data:
                    ind = data[col_name] in col_values
                    cnf.add(ind)
            # add data in case all the condition satisfied.
            if len(list(cnf)) == 1 and list(cnf)[0] is True:
                filtered_data_list.append(data)
        return filtered_data_list

    def calc_average_overlap_pct(self, all_model_records: list, config_data: dict):
        avg_matrix_list = []
        unique_model_names = sorted(
            list(set([x['model_name'] for x in all_model_records])))
        unique_model_names
        for model_name in unique_model_names:
            single_model_records = [
                x for x in all_model_records if x['model_name'] == model_name]
            # print(model_name)
            avg_matrix_result = self.__generate_overlap_pct(
                single_model_records, config_data)
            conf_matrix = {
                'model_name': model_name
            }
            conf_matrix.update(avg_matrix_result)
            # print(type(avg_matrix_list))
            avg_matrix_list.append(conf_matrix)
        return avg_matrix_list

    def __generate_overlap_pct(self, model_records, config_data):
        avg_matrix = {
            'total_documents': len(set([x['image_subpath'] for x in model_records])),
            'total_objects': len(model_records),
            'true_positive': -1,
            'true_negative': -1,
            'false_positive': -1,
            'false_negative': -1,
        }

        unique_sources = sorted(
            list(set([x['truth_source'] for x in model_records])))
        # print(unique_sources)
        full_match_records = [x['truth_overlap_pct'] for x in model_records if x['truth_source'] == 'match-found'
                              and x['truth_overlap_pct'] >= config_data['MIN_OVERLAP_PCT_FULL_MATCH']]
        partial_match_records = [x['truth_overlap_pct'] for x in model_records if x['truth_source'] == 'match-found'
                                 and x['truth_overlap_pct'] < config_data['MIN_OVERLAP_PCT_FULL_MATCH']
                                 and x['truth_overlap_pct'] >= config_data['MIN_OVERLAP_PCT_PARTIAL_MATCH']]
        low_match_records = [x['truth_overlap_pct'] for x in model_records if x['truth_source'] == 'match-found'
                             and x['truth_overlap_pct'] < config_data['MIN_OVERLAP_PCT_PARTIAL_MATCH']]
        # 'match-not-found', 'match-not-found;best-guess-applied'
        match_not_found_records = [x['truth_overlap_pct']
                                   for x in model_records if 'match-not-found' in x['truth_source']]
        not_extracted_records = [x['truth_overlap_pct']
                                 for x in model_records if 'entity-not-extracted' in x['truth_source']]

        true_positive_records = full_match_records
        # FP means "extra" tables found which don't exist (in truth data)
        false_positive_records = partial_match_records + \
            low_match_records + match_not_found_records
        # FN means "missing" tables not found which exist (in truth data)
        false_negative_records = not_extracted_records
        # Empty list as we're dealing with only one task which is table detection
        true_negative_records = []
        avg_matrix['true_positive'] = sum(
            true_positive_records)/len(true_positive_records) if len(true_positive_records) > 0 else 0
        avg_matrix['true_negative'] = len(true_negative_records)
        avg_matrix['false_positive'] = sum(false_positive_records)/len(
            false_positive_records) if len(false_positive_records) > 0 else 0
        avg_matrix['false_negative'] = sum(false_negative_records)/len(
            false_negative_records) if len(false_negative_records) > 0 else 0
        return avg_matrix

    def calc_confusion_matrix(self, all_model_records, config_data: dict):
        conf_matrix_list = []
        unique_model_names = sorted(
            list(set([x['model_name'] for x in all_model_records])))
        unique_model_names
        for model_name in unique_model_names:
            single_model_records = [
                x for x in all_model_records if x['model_name'] == model_name]
            # print(model_name)
            conf_matrix_result = self.__generate_model_confusion_matrix(
                single_model_records, config_data)
            conf_matrix = {
                'model_name': model_name
            }
            conf_matrix.update(conf_matrix_result)
            conf_matrix_list.append(conf_matrix)
        return conf_matrix_list

    def __generate_model_confusion_matrix(self, model_records, config_data: dict):
        confusion_matrix = {
            'total_documents': len(set([x['image_subpath'] for x in model_records])),
            'total_objects': len(model_records),
            'true_positive': -1,
            'true_negative': -1,
            'false_positive': -1,
            'false_negative': -1,
            'accuracy': -1,
            'precision': -1,
            'recall': -1
        }

        unique_sources = sorted(
            list(set([x['truth_source'] for x in model_records])))
        #     print(unique_sources)
        full_match_records = [x for x in model_records if x['truth_source'] == 'match-found'
                              and x['truth_overlap_pct'] >= config_data['MIN_OVERLAP_PCT_FULL_MATCH']]
        partial_match_records = [x for x in model_records if x['truth_source'] == 'match-found'
                                 and x['truth_overlap_pct'] < config_data['MIN_OVERLAP_PCT_FULL_MATCH']
                                 and x['truth_overlap_pct'] >= config_data['MIN_OVERLAP_PCT_PARTIAL_MATCH']]
        low_match_records = [x for x in model_records if x['truth_source'] == 'match-found'
                             and x['truth_overlap_pct'] < config_data['MIN_OVERLAP_PCT_PARTIAL_MATCH']]
        # 'match-not-found', 'match-not-found;best-guess-applied'
        match_not_found_records = [
            x for x in model_records if 'match-not-found' in x['truth_source']]
        not_extracted_records = [
            x for x in model_records if 'entity-not-extracted' in x['truth_source']]

        true_positive_records = full_match_records
        # FP means "extra" tables found which don't exist (in truth data)
        false_positive_records = partial_match_records + \
            low_match_records + match_not_found_records
        # FN means "missing" tables not found which exist (in truth data)
        false_negative_records = not_extracted_records
        # Empty list as we're dealing with only one task which is table detection
        true_negative_records = []
        confusion_matrix['true_positive'] = len(true_positive_records)
        confusion_matrix['true_negative'] = len(true_negative_records)
        confusion_matrix['false_positive'] = len(false_positive_records)
        confusion_matrix['false_negative'] = len(false_negative_records)
        confusion_matrix['accuracy'] = ((len(true_positive_records) + len(true_negative_records))
                                        / (len(true_positive_records) + len(true_negative_records)
                                        + len(false_positive_records) + len(false_negative_records)))
        confusion_matrix['precision'] = (len(true_positive_records)
                                         / (len(true_positive_records) + len(false_positive_records))) if (len(true_positive_records) + len(false_positive_records)) > 0 else 0
        confusion_matrix['recall'] = (len(true_positive_records)
                                      / (len(true_positive_records) + len(false_negative_records))) if (len(true_positive_records) + len(false_negative_records)) > 0 else 0

        return confusion_matrix
