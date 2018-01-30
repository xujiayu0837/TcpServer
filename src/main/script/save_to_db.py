import os
import time
import datetime
import pymysql

PATH = "/home/xujy/ihome"
PREFIX = "0C0004"
BUF = 256

# 获取mysql连接
def connect_db(host, port, user, passwd, db):
	conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
	return conn

def get_start_time_and_end_time(time_tuple):
	try:
		year = time_tuple[0]
		mon = time_tuple[1]
		day = time_tuple[2]
		hour = time_tuple[3]
		min = time_tuple[4]
		wday = time_tuple[6]
		yday = time_tuple[7]
		is_dst = time_tuple[8]
		start_time = int(time.mktime((year, mon, day, hour, min - 1, 0, wday, yday, is_dst)) * 1000)
		end_time = int(time.mktime((year, mon, day, hour, min, 0, wday, yday, is_dst)) * 1000)
		return start_time, end_time
	except Exception as e:
		# print("get_start_time_and_end_time() error")
		# return -1, -1
		raise e

def read_file():
	try:
		now = datetime.datetime.now()
		date = now.strftime("%Y%m%d")
		start_time, end_time = get_start_time_and_end_time(now.timetuple())
		# print(start_time)
		# print(end_time)

		conn = connect_db('localhost', 3306, 'root', 'qhiehome2017@123', 'ihome_relay')
		cursor = conn.cursor()

		# 更新动作表
		i = -1
		with open(os.path.join(PATH, date)) as fr:
			lines = fr.readlines()
			nums_line = len(lines)
			while i >= -nums_line:
				line = lines[i]
				line_list = line.split('|')
				data = line_list[0]
				ts = int(line_list[1])
				if ts >= end_time:
					i -= 1
					continue
				if ts < start_time:
					break
				if not data.startswith(PREFIX) or len(data) != 58:
					i -= 1
					continue
				device_id = data[:24]
				command = data[34:36]
				data_type = data[40:42]
				address = data[42:44]
				command_data = data[44:54]
				if command_data == "0000000000":
					i -= 1
					continue
				sql = """INSERT INTO t_relay_command(device_id, command, data_type, address, command_data, active_time, state) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
				cursor.execute(sql, (device_id, command, data_type, address, command_data, ts, 1))
				i -= 1

		# 更新心跳表
		i = -1
		with open(os.path.join(PATH, date)) as fr:
			lines = fr.readlines()
			nums_line = len(lines)
			while i >= -nums_line:
				line = lines[i]
				line_list = line.split('|')
				data = line_list[0]
				ts = int(line_list[1])
				if ts >= end_time:
					i -= 1
					continue
				if not data.startswith(PREFIX):
					i -= 1
					continue
				sql = """SELECT * FROM t_relay_heartbeat WHERE device_id = %s"""
				row_count = cursor.execute(sql, (data,))
				if row_count > 0:
					sql = """UPDATE t_relay_heartbeat SET active_time = %s WHERE device_id = %s"""
					cursor.execute(sql, (ts, data))
				else:
					sql = """INSERT INTO t_relay_heartbeat(device_id, active_time, state) VALUES(%s, %s, %s)"""
					cursor.execute(sql, (data, ts, 1))
				break
				i -= 1

		# 提交数据库事务
		conn.commit()
	except Exception as e:
		# 数据库回滚
		conn.rollback()
		raise e
	finally:
		# 关闭mysql连接
		conn.close()

if __name__ == '__main__':
	read_file()