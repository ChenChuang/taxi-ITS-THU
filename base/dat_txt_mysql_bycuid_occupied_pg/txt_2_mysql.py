import MySQLdb
import os
import re
import getpass

import common.config

DB_YEAR = "2009"

try:
    if not mysql_passwd:
        mysql_passwd = getpass.getpass("db password: ")
	conn = MySQLdb.connect(host = mysql_hostname, user = mysql_username, passwd = mysql_passwd, db = mysql_dbname, local_infile = 1)
	cursor = conn.cursor()

	all_f = os.listdir(txt_data_dir)
	for f in all_f:
		if not os.path.isfile(txt_data_dir + f):
			continue
		(f_name, f_ext) = os.path.splitext(f)
		if (not f_ext == '.txt') or (not re.compile(txt_reg).match(f_name)):
			print "skip file:",f
			continue

		print "processing file:",f

		text_f_path = txt_data_dir + f
		table_name = 'tb_' + DB_YEAR + f_name.split('_')[1]

		sql = r"CREATE TABLE IF NOT EXISTS " + table_name + r"""(
			CUID int not null,
			UTC int not null,
			LATITUDE int not null,
			LONGITUDE int not null,
			HEAD int not null,
			SPEED int not null,
			HEAVY int not null);"""
		cursor.execute(sql)
		conn.commit()

		sql = r"SELECT COUNT(*) FROM " + table_name
		cursor.execute(sql)
		count = cursor.fetchall()[0][0]
	
		skipthis = False	

		if not count:
			print "new table:" + table_name
		else:
			while True:
				r_input = raw_input("the table: " + table_name + " has " + str(count) + " records. would you like to add/reload/skip it? add/reload/skip: ")
				if r_input == "add":
					break
				elif r_input == "reload":
					sql = r"truncate table " + table_name
					n = cursor.execute(sql)
					conn.commit()
					break
				elif r_input == "skip":
					skipthis = True
					break
				else:
					print "input error"
		if not skipthis:
			print "loading",text_f_path,"to table",table_name,"..."
			sql= r"LOAD DATA LOCAL INFILE '" + text_f_path + r"' INTO TABLE " + table_name + r" FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'"
			cursor.execute(sql)
			conn.commit()
			print "completed"
		else:
			print "skip",text_f_path

	cursor.close()  
	conn.close()
except:
	pass
