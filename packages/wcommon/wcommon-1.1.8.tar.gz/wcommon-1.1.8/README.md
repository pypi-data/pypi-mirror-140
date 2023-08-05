# This is my common Python tool classes.


### /data/apps/public/conf.ini content like:
```
[mysql]
host=example.com
port=3306
user=username
passwd=password
database=test
charset=utf8mb4
```

### Find the localhost internal network ip:
```python
from wcommon import *
ip = getLocalIp()
hostname = getLocalHostname()
```

### Operate mysql data:
```python
mysql = Mysql(configuraion_file="/data/apps/public/conf.ini", section="mysql")

#query
rows = mysql.query("select * from example_table where status = %s order by id desc limit %s",(1,10))
for row in rows:
    print(row)
```