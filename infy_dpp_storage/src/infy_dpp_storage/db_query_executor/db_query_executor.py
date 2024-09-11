# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk
from neo4j import GraphDatabase, basic_auth

PROCESSOR_CONTEXT_DATA_NAME = "db_query_executor"


class DBQueryExecutor(infy_dpp_sdk.interface.IProcessor):
    """DB Query Executor Processor Implementation class"""

    def __init__(self) -> None:
        self.__logger = self.get_logger()

    def do_execute(self, document_data: infy_dpp_sdk.data.DocumentData,
                   context_data: dict, config_data: dict) -> infy_dpp_sdk.data.ProcessorResponseData:

        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        processor_config_data = config_data.get('DBQueryExecutor', {})
        failed_querys = []
        context_data = context_data if context_data else {}
        if context_data.get('db_query_generator').get('output'):
            for output in context_data.get('db_query_generator').get('output'):
                query_obj = output.get('queries')

                if processor_config_data.get('database_type') == 'neo4j':
                    neo4j_url = processor_config_data.get(
                        'database_credentials').get('database_url')
                    neo4j_user = processor_config_data.get(
                        'database_credentials').get('database_username')
                    neo4j_password = processor_config_data.get(
                        'database_credentials').get('database_password')

                    driver = GraphDatabase.driver(
                        neo4j_url, auth=basic_auth(neo4j_user, neo4j_password))

                    for query_index, query in query_obj.items():
                        with driver.session() as session:
                            try:
                                session.run(query)
                            except Exception as e:
                                self.__logger.debug(
                                    'Failed to execute query %s: %s', query_index, e)
                                failed_querys.append(query_index)

                    driver.close()

            context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                "failed_querys": failed_querys}

            processor_response_data.document_data = document_data
            processor_response_data.context_data = context_data

            return processor_response_data
