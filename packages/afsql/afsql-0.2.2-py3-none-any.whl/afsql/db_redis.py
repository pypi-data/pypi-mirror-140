# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     db_redis
   Description :
   Author :       asdil
   date：          2021/11/23
-------------------------------------------------
   Change Activity:
                   2021/11/23:
-------------------------------------------------
"""
__author__ = 'Asdil'
import redis


class Redis:
    """
    Redis类用于redis连接
    """
    def __init__(self, host, port, password=None, database=0, max_connections=2):
        """__init__(self):方法用于

        Parameters
        ----------
        host : str
            地址
        port : int
            端口
        password : str
            密码
        database : int
            数据库号
        Returns
        ----------
        """
        self.pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    password=password,
                                    db=database,
                                    max_connections=max_connections)


