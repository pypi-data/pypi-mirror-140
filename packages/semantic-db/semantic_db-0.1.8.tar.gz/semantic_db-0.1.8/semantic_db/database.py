import logging
import os
import sys
import bson
import faiss
import numpy as np

from typing import List, Dict, Any, Optional, Tuple
from pymongo import MongoClient

from ml_search_engine.filters import FilterCondition


class Database:
    def __init__(self, db_name: str, table: str, save_dir='/var/lobster/textsearch.index.dir') -> None:
        self.save_dir = save_dir
        self._searchindex = self._get_index(save_dir)
        self._db = self._get_database(db_name, table)

    def __del__(self):
        self._save_index()

    def _save_index(self):
        if self.save_dir is not None:
            index_path = os.path.join(self.save_dir, 'index.faiss')
            try:
                faiss.write_index(self._searchindex, index_path)
            except Exception as e:
                print(e, file=sys.stderr)

    @staticmethod
    def _get_database(db_name: str, table: str):
        server = os.getenv('DB_SERVER')
        if server is None:
            logging.info('DB_SERVER not set! use localhost')
            server = 'localhost'

        user = os.getenv('DB_USER')
        if user is None:
            logging.info('DB_USER not found! Use lobster')
            user = 'lobster'

        password = os.getenv('DB_PASS')
        if password is None:
            logging.info('DB_PASS not found! Use empty')
            password = ''

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        host = f"mongodb://{user}:{password}@{server}"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(host)

        # Create the database for our example (we will use the same database throughout the tutorial
        return client[db_name][table]

    @staticmethod
    def _get_index(save_dir: Optional[str]) -> faiss.Index:
        index_path = os.path.join(save_dir, 'index.faiss')
        if (save_dir is not None) and os.path.exists(index_path):
            return faiss.read_index(index_path)
        else:
            return faiss.IndexIDMap2(faiss.IndexFlatL2(512))

    def delete(self, doc: Dict[str, Any]):
        self._db.delete_one({'id': doc.get('id')})

    def put(self, documents: List[Dict[str, Any]], digests) -> List[Dict[str, Any]]:
        self._db.insert_many([doc for doc in documents])
        faiss_ids = []
        for doc in documents:
            self.delete(doc)
            faiss_ids.append(hash(doc.get('id')))

        faiss_ids = np.array(faiss_ids, dtype=np.int64)
        if len(faiss_ids) > 0:
            self._searchindex.remove_ids(faiss_ids)
            self._searchindex.add_with_ids(np.array(digests), faiss_ids)
            self._save_index()

        return documents

    @staticmethod
    def _filter(doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        stop_tags = ['nude', 'erotic', 'filmnudes', 'nudemodels', 'hasselblad', 'breasts',
                     'nakedinpublic', 'nakedbikeride']

        if (doc is not None) and (not (any([tag in doc.get('tags') for tag in stop_tags]))
                                  and not (doc.get('id') in ['49681632232', "49681632297", "49680807953"])):
            return doc
        else:
            return None

    def _search(self, sim_ids, filter):
        docs = self._db.find({'hash': {'$in': sim_ids}})
        docs_map = {d['hash']: d for d in docs}
        res = []
        presented_tags = set()
        for h in sim_ids:
            doc = docs_map.get(h)
            doc = self._filter(doc)

            if doc is None:
                res.append(None)
                continue

            t = ' '.join(sorted(doc['tags']))
            if t in presented_tags:
                res.append(None)
                continue
            else:
                presented_tags.add(t)

            if ((filter is not None) and filter(doc)) or filter is None:
                res.append(doc)
            else:
                res.append(None)

        return res

    def search_similar(
            self,
            encoded_queries: Optional[np.array],
            example_raw_docs: Optional[List[FilterCondition]] = None,
            treshold: float = 1.50,
            offset_limits: Optional[List[Tuple[int, int]]] = None,
            sort_by: Optional[List[str]] = None,
    ) -> List[List[object]]:

        radius, inds = self._searchindex.search(encoded_queries, 200)

        if example_raw_docs is None:
            example_raw_docs = [None] * len(encoded_queries)

        if offset_limits is None:
            offset = [0] * len(encoded_queries)
            limit = [100] * len(encoded_queries)
        else:
            offset, limit = zip(*offset_limits)

        if sort_by is None:
            sort_by = [None] * len(encoded_queries)

        res = []
        for rlv, ids, filter, ofs, lim, sortby in zip(radius, inds,
                                                      example_raw_docs, offset, limit, sort_by):

            ids = [bson.Int64(i) for i in ids]
            raw_documents = self._search(ids, filter)

            if len(raw_documents) == 0:
                continue

            if sortby == 'date':
                rlv = [d.get('created_at') if d is not None else 0 for d in raw_documents]

            rlv, documents = zip(*sorted(zip(rlv, raw_documents), key=lambda e: e[0]))
            documents = [doc for doc in documents if doc is not None]

            documents = documents[ofs:ofs + lim]
            res.append(documents)

        return res
