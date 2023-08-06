# -*- coding: UTF-8 -*-
# @Time : 2021/11/11 下午8:33 
# @Author : 刘洪波
from .cursors import Cursor
import requests


class Connection(object):
    def __init__(self, host: str, port: str, db: str, user: str, password: str):
        """
        连接数据库
        :param host:
        :param port:
        :param db:
        :param user:
        :param password:
        :return:
        """
        login_url = f'http://{host}:{port}/rest/login/{user}'
        headers = {'X-GraphDB-Password': password}
        response = requests.post(login_url, headers=headers)
        self.authorization = response.headers.get('Authorization')
        self.base_url = f'http://{host}:{port}/repositories/{db}'

    def cursor(self):
        if self.authorization is None:
            raise BaseException('GraphDB not connected')
        query_url = self.base_url + '?'
        update_url = self.base_url + '/statements?'
        return Cursor(query_url, update_url, self.authorization)

    def close(self):
        self.authorization = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

