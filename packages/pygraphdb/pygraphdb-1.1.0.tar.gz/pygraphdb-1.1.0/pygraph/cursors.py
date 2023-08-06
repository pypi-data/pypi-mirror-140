# -*- coding: UTF-8 -*-
# @Time : 2021/11/15 下午6:04 
# @Author : 刘洪波
import requests


class Cursor(object):
    def __init__(self, query_url, update_url, authorization):
        self.query_url = query_url
        self.update_url = update_url
        self.authorization = authorization

    def execute(self, sparql):
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

