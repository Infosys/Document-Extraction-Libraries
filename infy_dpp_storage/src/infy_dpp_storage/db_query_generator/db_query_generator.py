# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

PROCESSOR_CONTEXT_DATA_NAME = "db_query_generator"


class DBQueryGenerator(infy_dpp_sdk.interface.IProcessor):
    """DB Query Generator Processor Implementation class"""

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: infy_dpp_sdk.data.DocumentData,
                   context_data: dict, config_data: dict) -> infy_dpp_sdk.data.ProcessorResponseData:

        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        processor_config_data = config_data.get('DBQueryGenerator', {})
        output_list = []
        context_data = context_data if context_data else {}
        if context_data.get('reader').get('output'):
            # for output in context_data.get('reader').get('output'):
            output = context_data.get('reader').get('output')[0]
            model_output = output.get('model_output')
            self.__logger.debug('%s is the model output', model_output)
            data = None
            if isinstance(model_output, str):
                try:
                    data = json.loads(model_output)
                except json.JSONDecodeError:
                    pass
            elif isinstance(model_output, dict):
                data = model_output
            else:
                self.__logger.debug(
                    '%s is not a valid JSON', model_output)

            if processor_config_data.get('database_type') == 'neo4j':
                root_path = self.__file_sys_handler.get_bucket_name()
                schema_path = processor_config_data.get(
                    'schema_path')
                schema_path = root_path+schema_path
                with open(schema_path, 'r', encoding='UTF8') as schema_file:
                    schema = json.load(schema_file)
                reference_dict = {}
                if 'fields' in schema:
                    fields = schema['fields']
                    includes = fields.get('includes', [])
                    excludes = fields.get('excludes', [])

                    if includes:
                        temp_data = {key: value for key,
                                     value in data.items() if key in includes}
                    elif excludes:
                        temp_data = data.copy()
                        temp_data = {
                            key: value for key, value in temp_data.items() if key not in excludes}
                    else:
                        temp_data = data.copy()

                    for node in schema['nodes']:
                        name = node['name']
                        refers_to = node['refers_to']

                        if refers_to in temp_data:
                            value = temp_data[refers_to]

                            if 'properties' in node:
                                properties = node['properties']
                                parameters = {}

                                for key in properties:
                                    if key in temp_data:
                                        property_value = str(temp_data[key])
                                        parameters[key] = property_value

                                reference_dict[name] = {
                                    'value': str(value),
                                    'parameters': parameters
                                }
                            else:
                                reference_dict[name] = {
                                    'value': str(value)
                                }

                    if 'edges' in schema:
                        temp_edge = {}
                        for key, value in reference_dict.copy().items():
                            if isinstance(value, dict) and 'value' in value:
                                temp_edge[key] = value['value']

                            edges = schema['edges']
                            updated_edges = {}
                            for i, edge in enumerate(edges, start=1):
                                node1_key = edge['node1']
                                node2_key = edge['node2']
                                node1 = temp_edge.get(node1_key)
                                node2 = temp_edge.get(node2_key)
                                name = edge['name']
                                link_key = f'link{i}'
                                updated_edges[link_key] = f"{edge['node1']}:{node1};{edge['node2']}:{node2};{name}"

                            reference_dict['edges'] = updated_edges

                queries = {}
                for index, (label, properties) in enumerate(reference_dict.items(), start=1):
                    if label != 'edges':  # Exclude 'edges' from creating a new node
                        properties_str = ', '.join(
                            [f"{key}: {json.dumps(value)}" for key, value in properties.items() if key != 'parameters'])
                        parameters = properties.get('parameters', {})
                        if parameters:
                            properties_str += ', ' + \
                                ', '.join(
                                    [f"{key}: {json.dumps(value)}" for key, value in parameters.items()])
                        query = f'''MERGE (:{label.capitalize()} {{{properties_str.replace("'", "")}}})'''
                        queries[f"query_{index}"] = (query)

                if 'edges' in reference_dict:
                    edges = reference_dict['edges']
                    for index, (link, value) in enumerate(edges.items(), start=len(queries)+1):
                        node1, node2, relationship = value.split(';')
                        node1_label, node1_value = node1.split(':')
                        node2_label, node2_value = node2.split(':')
                        relationship_type = relationship.strip()
                        query = f'''MATCH (n1:{node1_label.capitalize()} {{value: '{node1_value.strip().replace("'", "")}'}}), (n2:{node2_label.capitalize()} {{value: '{node2_value.strip().replace("'", "")}'}}) CREATE (n1)-[:{relationship_type.upper()}]->(n2)'''
                        queries[f"query_{index}"] = (query)

                output_list.append({
                    "data_obejct": data,
                    "queries": queries
                })

                context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                    "output": output_list}

                processor_response_data.document_data = document_data
                processor_response_data.context_data = context_data

            return processor_response_data
