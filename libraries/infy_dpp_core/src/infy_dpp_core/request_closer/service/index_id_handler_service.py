# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import requests


class IndexIdHandlerService:

    def __init__(self) -> None:
        pass

    def post_index_id(self, indexer_response: dict, endpoint: str, payload: dict, headers: dict):
        index_id, index_name = '', ''
        if indexer_response:
            for index_type, index_data in indexer_response.items():
                if index_type == 'vector_db':
                    index_id = index_data.get('index_id', '')
                    break
                elif index_type == 'sparse_index':
                    index_id = index_data.get('index_id', '')
                    break
        if index_id:
            index_name = index_id.split('-', 1)[0]
        if index_id and index_name:
            payload['indexId'] = index_id
            payload['indexName'] = index_name
            try:
                response = requests.post(
                    endpoint, json=payload, headers=headers, timeout=30)
                if response.status_code == 200:
                    api_response = response.json()
                    if api_response.get('status') == 'Success' and api_response.get('data').get('status') == 'Created':
                        return True
                    else:
                        return False
                else:
                    raise RuntimeError("Failed to call endpoint")
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to call endpoint: {e}") from e
        else:
            raise ValueError("Index ID or Index Name is missing")
