# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Wrapper for ELASTIC SEARCH"""

from elasticsearch import Elasticsearch


class ElasticSearchService():
    '''Class for making CRUD operations on elasticsearch'''

    def __init__(self, db_server_url: str = '', authenticate: bool = True, username: str = '', password: str = '', verify_certs: bool = True, cert_fingerprint: str = '', ca_certs_path: str = '', index_id: str = '') -> None:
        self.__db_server_url = db_server_url
        self.__username = username
        self.__password = password
        self.__verify_certs = verify_certs
        self.__cert_fingerprint = cert_fingerprint
        self.__ca_certs_path = ca_certs_path
        self.__index_id = index_id
        self.__es_index = "idx-del-"+index_id

        if authenticate:
            self.es_client = Elasticsearch(
                [self.__db_server_url],
                http_auth=(self.__username, self.__password),
                verify_certs=self.__verify_certs,
                ca_certs=self.__ca_certs_path,
                ssl_show_warn=False,
                ssl_assert_fingerprint=self.__cert_fingerprint
            )
        else:
            self.es_client = Elasticsearch(
                [self.__db_server_url]
            )
        self.utils = ElasticSearchUtils()

    def check_index_exists(self):
        '''Check if index exists in elasticsearch'''
        response = self.es_client.indices.exists(index=self.__es_index)
        return response

    def create_new_index(self, vector_dimension: int):
        '''Create a new index in elasticsearch'''
        query = self.utils.get_query_create_schema(vector_dimension)
        response = self.es_client.indices.create(
            index=self.__es_index, body=query)
        return response

    def add_record(self, model_name: str, embedding: list, content: str, metadata: dict):
        '''Add data to the created index'''
        query = self.utils.get_query_add_record(
            self.__index_id, model_name, embedding, content, metadata)
        response = self.es_client.index(index=self.__es_index, body=query)
        return response

    def get_records(self):
        '''Retrieve all records form the index'''
        query = self.utils.get_query_get_records()
        response = self.es_client.search(index=self.__es_index, body=query)
        return response['hits']['hits']

    def delete_index(self):
        '''Delete the index'''
        response = self.es_client.indices.delete(index=self.__es_index)
        # Below code is for get_query_delete_record_by_id | Not Used
        # query = self.utils.get_query_delete_record_by_id()
        # response = self.es_client.delete_by_query(
        #     index=self.__es_index, body=query)
        return response

    def get_matches(self, model_name: str, embedding: list, filter_metadata: dict, top_k: int, pre_filter_fetch_k: int):
        '''Retrieve top matches for a query from the index'''
        query = self.utils.get_query_get_matches(
            model_name, self.__index_id, embedding, filter_metadata, top_k)
        response = self.es_client.search(index=self.__es_index, body=query)
        return response['hits']['hits']

    def get_custom_metadata_schema(self):
        '''Retrieve the schema for custom metadata'''
        query = self.utils.get_query_get_custom_metadata_schema(
            self.__index_id)
        response = self.es_client.search(index=self.__es_index, body=query)
        if response['hits']['hits']:
            all_keys = set()
            for hit in response['hits']['hits']:
                custom_metadata = hit['_source']['metadata'].get(
                    'custom_metadata', {})
                all_keys.update(custom_metadata.keys())

            schema = {key: '' for key in all_keys}
            return schema
        return {}


class ElasticSearchUtils():
    '''Class for making elastic search queries'''

    def __init__(self) -> None:
        pass

    def get_query_get_matches(self, model_name: str, index_id: str, embedding: list, filter_metadata: dict, top_k: int):
        '''Query for getting matches from elasticsearch index'''
        filters = [
            {
                "term": {
                    "p_model_name": model_name
                }
            },
            {
                "term": {
                    "p_index_id": index_id
                }
            }
        ]

        # Separate custom_metadata filters and general metadata filters
        custom_metadata_filter = {
            k.split('custom_metadata.')[1]: v for k, v in filter_metadata.items() if k.startswith('custom_metadata.')
        }
        general_filter = {
            k: v for k, v in filter_metadata.items() if not k.startswith('custom_metadata.')
        }

        # Add general metadata filters
        for key, value in general_filter.items():
            filters.append({
                "term": {
                    f"metadata.{key}": value
                }
            })
        # Add custom metadata filters
        for key, value in custom_metadata_filter.items():
            filters.append({
                "term": {
                    f"metadata.custom_metadata.{key}": value
                }
            })

        return {
            "_source": [
                "content",
                "metadata"
            ],
            "query": {
                "bool": {
                    "filter": filters,
                    "must": [
                        {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "l2norm(params.query_vector, 'embedding')",
                                    "params": {
                                        "query_vector": embedding
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "_score": {
                        "order": "asc"
                    }
                }
            ],
            "size": top_k
        }

    def get_query_create_schema(self, vector_dimension: int):
        '''Query for elasticsearch index(schema/mapping) creation'''
        return {
            "settings": {
                "number_of_replicas": 0,
                "index.blocks.write": False
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "p_model_name": {
                        "type": "keyword"
                    },
                    "p_index_id": {
                        "type": "keyword"
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": vector_dimension
                    },
                    "content": {
                        "type": "text"
                    },
                    "metadata": {
                        "type": "object",
                        "dynamic": True
                    }
                }
            }
        }

    def get_query_add_record(self, index_id: str, model_name: str, embedding: list, content: str, metadata: dict):
        '''Query for adding record to elasticsearch index'''
        return {
            "p_model_name": model_name,
            "p_index_id": index_id,
            "embedding": embedding,
            "content": content,
            "metadata": metadata
        }

    def get_query_get_records(self):
        '''Query for getting records from elasticsearch index'''
        return {
            "query": {
                "match_all": {}
            }
        }

    def get_query_delete_record_by_id(self):
        '''Query for deleting records from elasticsearch index. This is not used in the current implementation'''
        return {
            "query": {
                "term": {
                    "_id": ""
                }
            }
        }

    def get_query_get_custom_metadata_schema(self, index_id: str):
        '''Query for getting the schema of custom metadata from elasticsearch index'''
        return {
            "_source": [
                "metadata.custom_metadata"
            ],
            "query": {
                "term": {
                    "p_index_id": index_id
                }
            }
        }
