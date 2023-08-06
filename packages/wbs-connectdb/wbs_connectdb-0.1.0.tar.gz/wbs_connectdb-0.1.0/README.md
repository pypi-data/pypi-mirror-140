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

conn_info = Connection.Connection(
        host='xxxxxxxxxxxxxxxx',
        port=xxx,
        dbname='xxxxx',
        user='xxxx',
        password='xxxx'
)

# 返回连接对象
conn = conn_info.ConectPsql()
#创建游标
cur = conn.cursor()

# 务必释放资源
cur.close()
conn.close()
```
