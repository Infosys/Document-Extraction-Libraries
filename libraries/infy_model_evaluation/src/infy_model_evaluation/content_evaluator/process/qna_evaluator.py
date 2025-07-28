# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
This class is evaluating the QnA pair.
"""
import logging
import traceback
import concurrent.futures
from ...content_evaluator.interface import IMetricsProvider
from ...data import ContentEvaluatorReqData, ContentEvaluatorResData, MetricsData


class QnaEvaluator():
    """Class for Qna pair evaluation"""

    def __init__(self, metric_provider_obj_list: list[IMetricsProvider]) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__metric_provider_obj_list = metric_provider_obj_list

    def evaluate(self, content_evaluator_req_data: ContentEvaluatorReqData) -> ContentEvaluatorResData:
        """   This method does the processing required and initiates the evaluation."""
        metrics_data = None
        combined_metrics_data_dict = {}
        try:
            list_count = len(self.__metric_provider_obj_list)
            with concurrent.futures.ThreadPoolExecutor(max_workers=list_count) as executor:
                futures = []
                for metric_provider_obj in self.__metric_provider_obj_list:
                    futures.append(executor.submit(
                        metric_provider_obj.calculate_metrics,
                        content_evaluator_req_data))

                for future in concurrent.futures.as_completed(futures):
                    metrics_data = future.result()
                    if metrics_data is not None:
                        combined_metrics_data_dict.update(
                            metrics_data.__root__)

            content_evaluator_res_data = ContentEvaluatorResData(
                metrics=MetricsData(__root__=combined_metrics_data_dict))
        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e
        return content_evaluator_res_data
