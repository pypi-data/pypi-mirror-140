import psycopg2
import pymysql
import sys


class Connection:
    def __init__(self,**ConnectInfor):
        self.ConnectInfor = ConnectInfor

    # Postgresql
    def ConectPsql(self):
        try:
            conn = psycopg2.connect(
                host=self.ConnectInfor['host'],
                port=self.ConnectInfor['port'],
                dbname=self.ConnectInfor['dbname'],
                user=self.ConnectInfor['user'],
                password=self.ConnectInfor['password']
            )
            print('成功连至数据库')
            return conn
        except:
            print("连接失败")
            print(sys.exc_info())


    # Mysql
    def ConectMysql(self):
        try:
            conn = pymysql.connect(
                host=self.ConnectInfor['host'],
                port=self.ConnectInfor['port'],
                database=self.ConnectInfor['dbname'],
                user=self.ConnectInfor['user'],
                password=self.ConnectInfor['password']
            )
            print('成功连至数据库')
            return conn
        except:
            print("连接失败")
            print(sys.exc_info())
