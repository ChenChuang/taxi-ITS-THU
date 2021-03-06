import MySQLdb
import getpass
import os

import common.lib as lib
import common.config

fromdate = (2009,5,1)   #format:(year, month, day)
todate = (2009,5,30)   

fromtime = (0,0,0)  #24hour, format:(hour, minute, second)
totime = (23,59,59)  

tbnames = lib.dates_to_tbnames(fromdate, todate)
utcs = lib.times_to_utcs(fromdate, todate, fromtime, totime)

output_dir = lib.new_output_dir()
if output_dir == "":
	exit()
f_count = 1
l_count = 0
f = open(str(f_count) + '.txt', 'w')
print 'new file:',f.name

conn = MySQLdb.connect(host=mysql_hostname,user=mysql_username,passwd=getpass.getpass("db password: "),db=mysql_dbname)  
cursor = conn.cursor()

print "mysql connected."

for tbname, utc in zip(tbnames, utcs):	
	try:
		#sql = r"SELECT COUNT(*) FROM " + tbname
		#sql = r"SELECT COUNT(*) FROM " + tbname + r" WHERE UTC >= " + str(utc[0]) + r" AND " + r"UTC <= " + str(utc[1])
		sql = r"SELECT * FROM " + tbname + r" WHERE CUID = 1"

		print 'querying',tbname,'...',
		cursor.execute(sql)
		results = cursor.fetchall()
		print 'completed'

		for items in results:
			for item in items:
				f.write(str(int(item)) + ', ')
			f.write(os.linesep)
			l_count += 1
			if l_count >= query_output_lines:
				f.close()
				f_count += 1
				f = open(str(f_count) + '.txt', 'w')
				print 'new file:',f.name
				l_count = 0
		pass
	except Exception as e:
		print e
		pass 

cursor.close()  
conn.close()
f.close()
