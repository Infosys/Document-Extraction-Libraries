# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Wrapper for FAISS"""

import os
import json
import uuid
import numpy
import faiss


class FaissService():
    """Wrapper for FAISS"""

    def __init__(self, db_folder_path: str = '', index_name: str = '', index_secret_key: str = ''):
        self.__index = None
        self.__data_dict = None
        self.__map_dict = None  # Store relationship between index and data
        self.__secret_key_dict = {
            "secret_key": index_secret_key} if index_secret_key else {}
        # DB folder path
        self.__db_folder_path = db_folder_path
        # DB file names
        self.__index_file_name = f"{index_name}.faiss"
        self.__data_file_name = f"{index_name}.data.json"
        self.__map_file_name = f"{index_name}.map.json"
        self.__secret_key_file_name = f"{index_name}.metadata.json"
        # DB file paths
        self.__index_file_path = f"{self.__db_folder_path}/{self.__index_file_name}"
        self.__data_file_path = f"{self.__db_folder_path}/{self.__data_file_name}"
        self.__map_file_path = f"{self.__db_folder_path}/{self.__map_file_name}"
        self.__secret_key_file_path = f"{self.__db_folder_path}/{self.__secret_key_file_name}"

    def create_new(self, vector_dimension: int):
        """Create a new vector DB"""
        index = faiss.IndexFlatL2(vector_dimension)
        self.__index = index
        self.__data_dict, self.__map_dict = {}, {}

    def add_record(self, vector: numpy.ndarray, content: str, metadata: dict):
        """Add a record to vector DB"""
        index = self.__index
        data_dict, map_dict = self.__data_dict, self.__map_dict
        faiss.normalize_L2(vector)
        index.add(vector)
        index_id = str(index.ntotal - 1)
        data_id = str(uuid.uuid4())
        map_dict[index_id] = data_id
        data_dict[data_id] = {'content': content,
                              'metadata': metadata}

    def get_records(self, start: int = 0, end: int = -1, include_vector: bool = False) -> list:
        """Get records from vector DB
        Args:
            start (int): Start index
            end (int): End index. -1 indicates the end of the index
        """
        index = self.__index
        data_dict, map_dict = self.__data_dict, self.__map_dict
        _end = index.ntotal if end == -1 else end
        _end = min(index.ntotal, _end)
        records = []
        for i in range(start, _end):
            index_id = str(i)
            data_id = map_dict[index_id]
            vector = index.reconstruct(i)
            records.append({
                'id': data_id,
                'content': data_dict[data_id]['content'],
                'metadata': data_dict[data_id]['metadata'],
                'vector_size': len(vector),
            })
            if include_vector:
                records[len(records)-1]['vector'] = vector.tolist()
        return records

    def get_custom_metadata_schema(self):
        """Get the schema of the custom_metadata object within metadata"""
        data_dict = self.__data_dict
        if not data_dict:
            return {}

        schema = {}
        for data_id, data in data_dict.items():
            metadata = data.get('metadata', {})
            custom_metadata = metadata.get('custom_metadata', {})

            # Merge the current custom_metadata keys into the schema
            for key in custom_metadata.keys():
                if key not in schema:
                    schema[key] = ''
        return schema

    def export_db(self, save_file_path: str, start: int = 0, end: int = -1,
                  include_vector: bool = True) -> int:
        """Export the vector DB to a file"""
        records = self.get_records(start, end, include_vector)
        with open(save_file_path, 'w', encoding='utf-8') as file:
            json.dump(records, file, indent=4, ensure_ascii=False)
        return len(records)

    def search_records(self, vector: numpy.ndarray, top_k: int = 4,
                       filter_metadata: dict = None, fetch_k: int = 100):
        """Search for records in vector DB
        Args:
            vector: Query vector
            top_k: Number of documents to return
            filter_metadata: Metadata to filter the search results after fetching fetch_k records.
            fetch_k: Number of documents to fetch before filtering. Defaults to 100.
        """

        # query, filter=filter_metadata, k=top_k, fetch_k=pre_filter_fetch_k
        index = self.__index
        data_dict, map_dict = self.__data_dict, self.__map_dict
        faiss.normalize_L2(vector)
        # Step 1: Get fetch_k number of records
        _fetch_k = min(fetch_k, index.ntotal)
        distances, distance_ids = index.search(vector, _fetch_k)
        records = []
        precomputed_filters, general_filter = {},{}
        
        # get filters if filter_metadata is provided
        if filter_metadata:
            custom_metadata_filter = {
                k.split('custom_metadata.')[1]: v for k, v in filter_metadata.items() if k.startswith('custom_metadata.')
            }
            precomputed_filters = {
                key: set(value if isinstance(value, list) else [value])
                for key, value in custom_metadata_filter.items()
            }
            general_filter = {
                k: v for k, v in filter_metadata.items() if not k.startswith('custom_metadata.')
            }
        # Step 2: Apply filter, if available
        for distance, distance_id in zip(distances[0], distance_ids[0]):
            index_id = str(distance_id)
            data_id = map_dict[index_id]
            metadata = data_dict[data_id]['metadata']
            if filter_metadata:
                # Check general metadata
                if general_filter and not general_filter.items() <= metadata.items():
                    continue

                # Check custom_metadata
                custom_metadata = metadata.get('custom_metadata', {})
                if not all(
                    key in custom_metadata and precomputed_filters[key] & set(custom_metadata.get(key, '').split())
                    for key in precomputed_filters
                ):
                    continue
            
            records.append({
                'distance': distance,
                'content': data_dict[data_id]['content'],
                'metadata': metadata
            })
            
        if not filter_metadata or not custom_metadata_filter:
            return records[:top_k]
            
        # Step 3: Group records by custom_metadata filter values
        grouped_records = {}
        if precomputed_filters:
            grouped_records = {value: [] for values in precomputed_filters.values() for value in values}
            for record in records:
                custom_metadata = record['metadata'].get('custom_metadata', {})
                for key, values in precomputed_filters.items():
                    record_values = set(custom_metadata.get(key, '').split())
                    for value in values:
                        if value in record_values:
                            grouped_records[value].append(record)
                            break

        # Step 4: Alternate between groups 
        alternated_records = []
        if grouped_records:
            group_keys = list(grouped_records.keys())
            group_index = 0
            while len(alternated_records) < top_k:
                has_records = False
                for _ in range(len(group_keys)):
                    key = group_keys[group_index]
                    if grouped_records[key]:
                        alternated_records.append(grouped_records[key].pop(0))
                        has_records = True
                        if len(alternated_records) == top_k:
                            break
                    group_index = (group_index + 1) % len(group_keys)
                if not has_records:
                    break
            
        # Step 5: Sort alternated records
            alternated_records.sort(key=lambda x: x['distance'])

        return alternated_records

    def load_local(self):
        """Load the vector DB from local file system"""
        self.__validate_fields()
        index_file_path = self.__index_file_path
        data_file_path, map_file_path, secret_key_file_path = self.__data_file_path, self.__map_file_path, self.__secret_key_file_path

        if os.path.exists(secret_key_file_path):
            with open(secret_key_file_path, 'r', encoding='utf-8') as file:
                secret_key_dict = json.load(file)
                stored_secret_key = secret_key_dict.get("secret_key")
                if self.__secret_key_dict is not None and stored_secret_key == self.__secret_key_dict.get("secret_key", ""):
                    index = faiss.read_index(index_file_path)
                    data_dict, map_dict = {}, {}
                    with open(data_file_path, 'r', encoding='utf-8') as file:
                        data_dict = json.load(file)
                    with open(map_file_path, 'r', encoding='utf-8') as file:
                        map_dict = json.load(file)
                    self.__index = index
                    self.__data_dict = data_dict
                    self.__map_dict = map_dict
                else:
                    raise ValueError(
                        "Secret key provided does not match the collection, please provide correct secret key.")
        else:
            index = faiss.read_index(index_file_path)
            data_dict, map_dict = {}, {}
            with open(data_file_path, 'r', encoding='utf-8') as file:
                data_dict = json.load(file)
            with open(map_file_path, 'r', encoding='utf-8') as file:
                map_dict = json.load(file)
            self.__index = index
            self.__data_dict = data_dict
            self.__map_dict = map_dict

    def save_local(self):
        """Save the vector DB to the local file system"""
        if not os.path.exists(self.__db_folder_path):
            os.makedirs(self.__db_folder_path)
        index_file_path = self.__index_file_path
        data_file_path, map_file_path, secret_key_file_path = self.__data_file_path, self.__map_file_path, self.__secret_key_file_path
        index = self.__index
        data_dict, map_dict, secret_key_dict = self.__data_dict, self.__map_dict, self.__secret_key_dict
        faiss.write_index(index, index_file_path)
        with open(data_file_path, 'w', encoding='utf-8') as file:
            json.dump(data_dict, file, indent=4, ensure_ascii=False)
        with open(map_file_path, 'w', encoding='utf-8') as file:
            json.dump(map_dict, file, indent=4, ensure_ascii=False)
        if secret_key_dict is not None and secret_key_dict:
            if not os.path.exists(secret_key_file_path):
                with open(secret_key_file_path, 'w', encoding='utf-8') as file:
                    json.dump(secret_key_dict, file, indent=4, ensure_ascii=False)

    def get_record_count(self):
        """Get the record count"""
        return self.__index.ntotal

    def delete_local(self):
        """Load the vector DB from local file system"""
        self.__validate_fields()
        index_file_path, data_file_path, map_file_path, secret_key_file_path = self.__index_file_path, self.__data_file_path, self.__map_file_path, self.__secret_key_file_path
        records_list = []
        if os.path.exists(secret_key_file_path):
            with open(secret_key_file_path, 'r', encoding='utf-8') as file:
                secret_key_dict = json.load(file)
                stored_secret_key = secret_key_dict.get("secret_key")
                if self.__secret_key_dict is not None and stored_secret_key == self.__secret_key_dict.get("secret_key", ""):
                    records_list.append(index_file_path)
                    records_list.append(data_file_path)
                    records_list.append(map_file_path)
                    records_list.append(secret_key_file_path)
                else:
                    raise ValueError(
                        "Secret key provided does not match the collection, please provide correct secret key.")
        else:
            records_list.append(index_file_path)
            records_list.append(data_file_path)
            records_list.append(map_file_path)

        return records_list

    # ----------- Private Methods ------------

    def __validate_fields(self):
        """Validate the fields"""
        if not self.__db_folder_path or not os.path.exists(self.__db_folder_path):
            message = f"'db_folder_path = {self.__db_folder_path}' does not exist."
            raise ValueError(message)
        if not self.__index_file_name or not os.path.exists(self.__index_file_path):
            message = f"'index_file_path = {self.__index_file_path}' does not exist."
            raise ValueError(message)
        if not self.__data_file_name or not os.path.exists(self.__data_file_path):
            message = f"'data_file_path = {self.__data_file_path}' does not exist."
            raise ValueError(message)
        if not self.__map_file_name or not os.path.exists(self.__map_file_path):
            message = f"'map_file_path = {self.__map_file_path}' does not exist."
            raise ValueError(message)
