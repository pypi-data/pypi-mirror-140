# 连接数据库工具包
## 支持类型
- Mysql
- Postgresql
- Hologres
## 使用方法
1. 下载
```
pip install -i https://pypi.org/project wbs-connectdb
```
2. 使用
```python
import Connection_Tool.Connection as Connection

# mysql
mysql= Connection.Mysql(
        host='127.0.0.1',
        port=3306,
        dbname='',
        user='root',
        password='root')

# psql
psql = Connection.Psql(
        host='127.0.0.1',
        port=5433,
        dbname='db',
        user='postgres',
        password='admin'
)
print(psql.ExecuteSql('select 1'))
print(mysql.ExecuteSql('select 2'))
```
