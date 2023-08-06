### shell

``` shell
from amhhandler import shell


cmd = "ls /tmp"
result, rcode = shell.run(cmd)
if rcode == 0:
    print(result)
else:
    print('execute error: {0}'.format(result))
```

### mysql

``` shell
from amhhandler import mysql


dbconfig = {"host":"127.0.0.1","port":3306, "user":"admin", "password":"123456", "db":"mysql"}

dbHandler = mysql.Conn(**dbconfig)
sql = "select * from mysql.user where user='admin';"
result = dbHandler.select(sql)

```

### ding ding robot


### logging
```shell
log = logger.log2file('/tmp/run.log')
log.info('execute log')
```
