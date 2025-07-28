# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


class QueryHybridRrf():
    def __init__(self, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def query_rrf(self, queries_list):
        for query in queries_list:
            if len(query['top_k_matches']) > 1:
                top_k = query['top_k']
                sparseindex_matches, vectordb_matches = [], []
                for match in query['top_k_matches']:
                    if 'sparseindex' in match:
                        sparseindex_matches = match.get('sparseindex')
                    elif 'vectordb' in match:
                        vectordb_matches = match.get('vectordb')

                sparse_list = []
                vector_list = []

                rank = 1
                for item in sparseindex_matches:
                    if 'message' in item:
                        continue
                    sparse_list.append({
                        'chunk_id': item.get('meta_data', {}).get('chunk_id', ''),
                        'rank': rank,
                        'context': item.get('content'),
                        'meta_data': item.get('meta_data', {}),
                        'file_path': item.get('file_path', ''),
                        'method': 'sparseindex'
                    })
                    rank += 1

                rank = 1
                for item in vectordb_matches:
                    if 'message' in item:
                        continue
                    vector_list.append({
                        'chunk_id': item.get('meta_data', {}).get('chunk_id', ''),
                        'rank': rank,
                        'context': item.get('content'),
                        'meta_data': item.get('meta_data', {}),
                        'file_path': item.get('file_path', ''),
                        'method': 'vectordb'
                    })
                    rank += 1

                rrf_scores = self.calculate_rrf(
                    sparse_list, vector_list)

                rrf_matches = []
                for record in rrf_scores:
                    rrf_match = {
                        "file_path": record['file_path'],
                        "score": record['score'],
                        "min_distance": -1,
                        "max_distance": -1,
                        "content": record['context'],
                        "meta_data": record['meta_data'],
                    }
                    rrf_matches.append(rrf_match)

                rrf_matches = rrf_matches[:top_k]
                query['top_k_matches'].append({'rrf': rrf_matches})
            else:
                rrf_matches = []
                rrf_match = {
                    "file_path": '',
                    "score": '',
                    "min_distance": -1,
                    "max_distance": -1,
                    "content": '',
                    "meta_data": '',
                    "message": "Less than 2 index matches available for RRF calculation, atleast 2 matches are required"
                }
                rrf_matches.append(rrf_match)
                query['top_k_matches'].append({'rrf': rrf_matches})

        return queries_list

    def calculate_rrf(self, sparse_list, vector_list):
        combined_scores = {}
        k = 60

        combined_list = sparse_list + vector_list

        for item in combined_list:
            chunk_id = item['chunk_id']
            rank = item['rank']
            rrf_score = 1 / (rank + k)
            if chunk_id in combined_scores:
                combined_scores[chunk_id]['score'] += rrf_score
                combined_scores[chunk_id]['methods'].add(item['method'])
            else:
                combined_scores[chunk_id] = {
                    'chunk_id': chunk_id,
                    'score': rrf_score,
                    'context': item['context'],
                    'meta_data': item['meta_data'],
                    'file_path': item['file_path'],
                    'methods': {item['method']}
                }

        sorted_items = sorted(combined_scores.values(),
                              key=lambda x: x['score'], reverse=True)

        rrf_scores = [{
            'chunk_id': item['chunk_id'],
            'score': item['score'],
            'context': item['context'],
            'meta_data': item['meta_data'],
            'file_path': item['file_path'],
            'methods': list(item['methods'])
        } for item in sorted_items]

        return rrf_scores
