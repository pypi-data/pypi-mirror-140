# This is my common Python tool classes.

### Find the localhost internal network ip:
```python
from wcommon import *
ip = getLocalIp()
hostname = getLocalHostname()

mysql = Mysql(section="mysql")

```

### Operate mysql data:
```python
mysql = Mysql(configuraion_file="/data/apps/public/conf.ini", section="mysql")

#query
rows = mysql.query("select * from example where status = %s order by id desc limit %s",(1,10))
for row in rows:
    print(row)
```