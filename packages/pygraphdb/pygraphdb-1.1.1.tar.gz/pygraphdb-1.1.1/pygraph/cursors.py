# -*- coding: UTF-8 -*-
# @Time : 2021/11/15 下午6:04 
# @Author : 刘洪波
import requests


class Cursor(object):
    def __init__(self, query_url, update_url, authorization):
        self.query_url = query_url
        self.update_url = update_url
        self.authorization = authorization

    def execute(self, sparql: str):
        """
        执行 sparql
        :param sparql: 例 "SELECT ?s ?p ?o WHERE {?s ?p ?o .} LIMIT 100"
        :return:
        """
        if self.query_url is None or self.update_url is None:
            raise BaseException('Cursor is closed')
        use_type, params = self.check_key(sparql)
        if use_type == 'query':
            return requests.get(self.query_url, headers={'Authorization': self.authorization}, params=params).text
        elif use_type == 'update':
            return requests.post(self.update_url, headers={'Authorization': self.authorization}, data=params).text

    def download_data(self, file_path: str = None):
        """
        下载数据
        :param file_path: 文件路径  例：'./file.rdf' 或 './file.json'
        :return:
        """
        if '.rdf' in file_path:
            params = {'Accept': 'application/rdf+xml'}
        elif '.json' in file_path:
            params = {'Accept': 'application/rdf+json'}
        else:
            raise ValueError('file_path is error, Only RDF and JSON formats are supported')
        data = requests.get(self.update_url, headers={'Authorization': self.authorization}, params=params)
        if file_path:
            with open(file_path, "wb") as fp:
                itr = data.iter_content()
                for content in itr:
                    fp.write(content)
        else:
            return data

    @staticmethod
    def check_key(sparql):
        """
        校验sparql里的关键字
        :param sparql:
        :return:
        """
        upper_sparql = sparql.upper()
        query = ['SELECT', 'CONSTRUCT', 'ASK', 'DESCRIBE']
        update = ['INSERT', 'DELETE']
        for q in query:
            if q in upper_sparql:
                params = {'query': sparql}
                return 'query', params
        for u in update:
            if u in upper_sparql:
                params = {'update': sparql, 'infer': True, 'sameAs': True}
                return 'update', params
        raise ValueError('sparql error, Keyword deletion')

    def close(self):
        self.query_url = None
        self.update_url = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

