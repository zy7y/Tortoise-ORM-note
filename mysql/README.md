# docker 搭建 MySQL 主从

> 参考链接：https://www.cnblogs.com/cao-lei/p/13606945.html

## 容器搭建

m1 / arm 执行： `docker-compose -f docker-compose-m1.yml up -d`
windows / inter: `docker-compose up -d`

```shell
# 进入容器执行，开启navicat 远程访问
mysql -uroot -p
use mysql;
UPDATE user SET host = '%' WHERE user ='root';
flush privileges; #
```

## 主从配置

### [master mysql](sqls/master.sql)

```sql
# 创建用户
create user 'slave'@'%' identified with mysql_native_password by '123456';

# 授权
grant replication slave on *.* to 'slave'@'%';

# 刷新权限
flush privileges;

# 查询server_id值
show variables like 'server_id';

# 也可临时（重启后失效）指定server_id的值（主从数据库的server_id不能相同）
set global server_id = 1;

# 查询Master状态，并记录File和Position的值
show master status;
```

![](https://cdn.nlark.com/yuque/0/2022/png/1624081/1668430904760-be384acd-85ef-4974-adc7-b16addbd285b.png?x-oss-process=image%2Fresize%2Cw_1500%2Climit_0)

### [slave mysql](sqls/slave.sql)

```sql
# 查询server_id值
show variables like 'server_id';

# 也可临时（重启后失效）指定server_id的值（主从数据库的server_id不能相同）
set global server_id = 2;

# 若之前设置过同步，请先重置
stop slave;
reset slave;

# 设置主数据库
change master to master_host='192.168.58.105',master_port=3306,master_user='slave',master_password='password',master_log_file='mysql-bin.000003',master_log_pos=2179;

# 开始同步
start slave;

# 若出现错误，则停止同步，重置后再次启动
stop slave;
reset slave;
start slave;

# 查询Slave状态
show slave status
```

### master_host

![](https://cdn.nlark.com/yuque/0/2022/png/1624081/1668433849748-584fe538-2818-4c7a-9d49-ae57d4024023.png?x-oss-process=image%2Fresize%2Cw_1300%2Climit_0)

## Result

![](https://cdn.nlark.com/yuque/0/2022/png/1624081/1668434243211-f68c5c36-aeb8-4f92-99f5-5c350148e5a2.png?x-oss-process=image%2Fresize%2Cw_1418%2Climit_0)
