# 查询server_id值
show variables like 'server_id';

# 也可临时（重启后失效）指定server_id的值（主从数据库的server_id不能相同）
set global server_id = 2;

# 若之前设置过同步，请先重置
stop slave;
reset slave;

# 设置主数据库
change master to master_host='192.168.58.105',master_port=3306,master_user='slave',master_password='123456',master_log_file='mysql-bin.000003',master_log_pos=2179;

# 开始同步
start slave;

# 若出现错误，则停止同步，重置后再次启动
stop slave;
reset slave;
start slave;

# 查询Slave状态
show slave status