# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Wrapper for BM25S"""

import os
import json
import bm25s
import nltk
from nltk.corpus import stopwords


class Bm25sService():
    """Wrapper for BM25S"""

    def __init__(self, fs_handler_obj, db_folder_path: str = '', local_db_folder_path: str = '', index_name: str = '', index_secret_key: str = ''):
        self.__fs_handler = fs_handler_obj
        # local_db_folder_path(abs) & db_folder_path(rel)
        self.__local_db_folder_path = local_db_folder_path
        self.__db_folder_path = db_folder_path
        # index_name & paths
        self.__index_name = index_name
        self.__local_index_folder_path = f"{self.__local_db_folder_path}/{self.__index_name}"
        self.__index_folder_path = f"{self.__db_folder_path}/{self.__index_name}"
        # secret_key_dict & paths
        self.__secret_key_dict = {
            "secret_key": index_secret_key} if index_secret_key else {}
        self.__secret_key_file_name = f"{index_name}.metadata.json"
        self.__local_secret_key_file_path = f"{self.__local_db_folder_path}/{self.__secret_key_file_name}"
        self.__secret_key_file_path = f"{self.__db_folder_path}/{self.__secret_key_file_name}"

    def create_new(self, nltk_data_dir: str, chunk_list: list, corpus: list):
        """Create a new sparse DB"""
        nltk.data.path.append(nltk_data_dir)
        stop_words = set(stopwords.words('english'))
        chunk_tokens = bm25s.tokenize(
            chunk_list, lower=True, stopwords=stop_words)
        retriever = bm25s.BM25(corpus=corpus)
        retriever.index(chunk_tokens)
        return retriever

    def save_local(self, retriever):
        """Save the sparse DB to the local file system"""
        if self.__index_name:
            if not os.path.exists(self.__local_index_folder_path):
                db_folder_path = self.__index_folder_path
                self.__fs_handler.create_folders(db_folder_path)
                local_folder_path = self.__local_index_folder_path
                retriever.save(local_folder_path)
                if self.__secret_key_dict is not None and self.__secret_key_dict:
                    if not os.path.exists(self.__local_secret_key_file_path):
                        with open(self.__local_secret_key_file_path, 'w', encoding='utf-8') as file:
                            json.dump(self.__secret_key_dict, file, indent=4,ensure_ascii=False)
            else:
                db_folder_path = self.__index_folder_path
                self.__fs_handler.create_folders(db_folder_path)
                local_folder_path = self.__local_index_folder_path
                retriever.save(local_folder_path)
        else:
            raise ValueError("Please provide collection_name")

    def load_local(self):
        """Load the sparse DB from local file system"""
        if os.path.exists(self.__local_secret_key_file_path):
            with open(self.__local_secret_key_file_path, 'r', encoding='utf-8') as file:
                secret_key_dict = json.load(file)
                stored_secret_key = secret_key_dict.get("secret_key")
                if self.__secret_key_dict is not None and stored_secret_key == self.__secret_key_dict.get("secret_key", ""):
                    load_retriever = bm25s.BM25.load(
                        save_dir=self.__local_index_folder_path, load_corpus=True, allow_pickle=True)
                else:
                    raise ValueError(
                        "Secret key provided does not match the collection, please provide correct secret key.")
        else:
            load_retriever = bm25s.BM25.load(
                save_dir=self.__local_index_folder_path, load_corpus=True)

        return load_retriever

    def add_record(self, retriever, nltk_data_dir, chunk_list, corpus):
        """Add a record to sparse DB"""
        nltk.data.path.append(nltk_data_dir)
        stop_words = set(stopwords.words('english'))
        combined_corpus = []
        chunk_list = []
        for doc in retriever.corpus:
            combined_corpus.append(doc)
        combined_corpus = retriever.corpus + corpus
        for doc in combined_corpus:
            chunk_list.append(doc['text'])
        chunk_tokens = bm25s.tokenize(
            chunk_list, lower=True, stopwords=stop_words)
        retriever = bm25s.BM25(corpus=combined_corpus)
        retriever.index(chunk_tokens)
        return retriever

    def get_records(self, retriever) -> list:
        """Get records from sparse DB"""
        records = []
        corpus_list = retriever.corpus
        for doc in corpus_list:
            records.append({
                'content': doc['text'],
                'metadata': doc['metadata'],
            })
        return records

    def search_records(self, retriever, nltk_data_dir, query, top_k, pre_filter_fetch_k) -> list:
        """Get matches from sparse DB"""
        sparse_retriever = retriever
        nltk.data.path.append(nltk_data_dir)
        stop_words = set(stopwords.words('english'))
        query_tokens = bm25s.tokenize(
            [query], lower=True, stopwords=stop_words)
        records = []
        k = pre_filter_fetch_k
        while k > 0:
            try:
                records = sparse_retriever.retrieve(
                    query_tokens, k=k, sorted=True, return_as="tuple")
                return records
            except ValueError:
                if k == pre_filter_fetch_k:
                    k = top_k*2 if top_k*2 < pre_filter_fetch_k else pre_filter_fetch_k-1
                else:
                    k -= 1
        return records

    def delete_local(self):
        """Delete the sparse DB collection from local file system"""
        records_dict = {}
        if os.path.exists(self.__local_secret_key_file_path):
            with open(self.__local_secret_key_file_path, 'r', encoding='utf-8') as file:
                secret_key_dict = json.load(file)
                stored_secret_key = secret_key_dict.get("secret_key")
                if self.__secret_key_dict is not None and stored_secret_key == self.__secret_key_dict.get("secret_key", ""):
                    records_dict['folder_path'] = self.__local_index_folder_path
                    records_dict['secret_key_path'] = self.__secret_key_file_path
                else:
                    raise ValueError(
                        "Secret key provided does not match the collection, please provide correct secret key.")
        else:
            records_dict['folder_path'] = self.__local_index_folder_path

        return records_dict
