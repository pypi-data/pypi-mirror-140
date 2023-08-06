# -*- coding: UTF-8 -*-
# @Time : 2021/11/11 下午8:16 
# @Author : 刘洪波


def connect(host, port, db, user, password):
    from .connections import Connection
    return Connection(host, port, db, user, password)




