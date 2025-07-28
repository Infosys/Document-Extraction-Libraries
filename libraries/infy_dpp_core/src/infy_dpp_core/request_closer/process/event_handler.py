# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from ..service.index_id_handler_service import IndexIdHandlerService


class EventHandler:
    def __init__(self, event_config: dict):
        self.success_config = event_config.get('success', [])
        self.failure_config = event_config.get('failure', [])

    def handle_event(self, indexer_response: dict):
        response_list = []
        for event in self.success_config:
            if event.get('enabled', False):
                if event.get('name') == 'IndexIdHandler':
                    endpoint = event.get('api_endpoint', '')
                    payload = event.get('payload', {})
                    headers = event.get('headers', {})
                    index_id_handler_service = IndexIdHandlerService()
                    response = index_id_handler_service.post_index_id(
                        indexer_response, endpoint, payload, headers)
                    response_list.append({event.get('name'): response})

        for event in self.failure_config:
            pass

        return response_list
