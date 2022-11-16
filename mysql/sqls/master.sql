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