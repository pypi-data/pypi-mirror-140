import psycopg2
import pymysql
import sys



class Connection:
    def __init__(self,**ConnectInfor):
        self.ConnectInfor = ConnectInfor

    def ExecuteSql(self,sql):
        pass

class Psql(Connection):

    # 连接Postgresql
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
    #  执行sql
    def ExecuteSql(self,sql):
        conn = self.ConectPsql()
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data


class Mysql(Connection):
    # 连接Mysql
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

   #  执行sql
    def ExecuteSql(self,sql):
        conn = self.ConectMysql()
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data