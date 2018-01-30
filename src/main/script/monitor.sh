#!/bin/sh
proc_name="tcp-server.jar" # 进程名

# 查询进程数量
proc_num()
{  
    num=`ps -ef | grep $proc_name | grep -v grep | wc -l`  
    return $num  
}  
  
proc_num
# 获取进程数量
number=$?
# 如果进程数量为0
if [ $number -eq 0 ]
# 重新启动进程
then
    java -jar /home/xujy/ihome/jar/tcp-server.jar 9001 /home/xujy/ihome/
fi