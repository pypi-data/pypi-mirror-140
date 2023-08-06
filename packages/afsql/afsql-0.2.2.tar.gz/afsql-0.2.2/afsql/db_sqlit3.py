# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     myslite3
   Description :
   Author :       asdil
   date：          2022/2/25
-------------------------------------------------
   Change Activity:
                   2022/2/25:
-------------------------------------------------
"""
__author__ = 'Asdil'
import sqlite3


class Sqlit3:
    """
    Sqlit3类用于存储临时数据
    """
    def __init__(self, db_address):
        """__init__(self):方法用于

        Parameters
        ----------
        db_address : str
            数据库地址 eg: /xxx/xxx/xxx.db

        Returns
        ----------
        """
        self.drive = sqlite3.connect(db_address, check_same_thread=False)

    def close_all(self):
        """close方法用于关闭数据库连接
        """
        self.drive.close()

    def select_all(self, sql, param=None):
        """excute方法用于查询数据

        Parameters
        ----------
        sql : str
            sql查询语句
        param: list or tuple or None
            查询参数
        Returns
        ----------
        """
        cursor = self.drive.cursor()
        if param is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, param)
        ret = cursor.fetchall()
        cursor.close()
        return ret

    def select_one(self, sql, param=None):
        """excute方法用于查询数据

        Parameters
        ----------
        sql : str
            sql查询语句
        param: list or tuple or None
            查询参数
        Returns
        ----------
        """
        cursor = self.drive.cursor()
        if param is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, param)
        ret = cursor.fetchone()
        cursor.close()
        return ret

    def excute(self, sql, param=None):
        """excute方法用于查询数据库

        Parameters
        ----------
        sql: str
            sql语句
        param: list or tuple or None
            查询参数
        Returns
        ----------
        """
        cursor = self.drive.cursor()
        try:
            if param is None:
                cursor.execute(sql)
            else:
                if type(param) is list:
                    cursor.executemany(sql, param)
                else:
                    cursor.execute(sql, param)
            count = self.drive.total_changes
            self.drive.commit()
            cursor.close()
        except Exception as e:
            print(e)
            cursor.close()
            return False
        if count > 0:
            return True
        else:
            return False
