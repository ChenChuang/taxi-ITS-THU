import MySQLdb
import getpass
import os

import common.lib as lib
import common.config

fromdate = (2009,5,1)   #format:(year, month, day)
todate = (2009,5,30)   

tbnames = lib.dates_to_tbnames(fromdate, todate)

if not mysql_passwd:
    mysql_passwd = getpass.getpass("db password: ")
conn = MySQLdb.connect(host = mysql_hostname, user = mysql_username, passwd = mysql_passwd, db = mysql_dbname)
cursor = conn.cursor()

print "mysql connected."

max_cuid = 8602
#max_cuid = 1

r_counter = 0

for query_cuid in range(1, max_cuid + 1):
	output_dir = lib.new_output_dir_as(query_output_dir + 'CUID_' + str(query_cuid) + '/')
	if output_dir == "":
		exit()
	f_count = 1
	l_count = 0
	f = open(output_dir + str(f_count) + '.txt', 'w')
	#print 'new file:',f.name

	print 'CUID =',str(query_cuid),'...',

	for tbname in tbnames:	
		try:
			#sql = r"SELECT MAX(CUID) FROM " + tbname
			#sql = r"SELECT COUNT(*) FROM " + tbname + r" WHERE UTC >= " + str(utc[0]) + r" AND " + r"UTC <= " + str(utc[1])
			sql = r"SELECT * FROM " + tbname + r" WHERE CUID = " + str(query_cuid) + " ORDER BY UTC"

			#print 'querying',tbname,'...',
			cursor.execute(sql)
			results = cursor.fetchall()
			#print 'completed'

			for items in results:
				for item in items:
					f.write(str(int(item)) + ', ')
				r_counter += 1
				f.write(os.linesep)
				l_count += 1
				if l_count >= query_output_lines:
					f.close()
					f_count += 1
					f = open(output_dir + str(f_count) + '.txt', 'w')
					#print 'new file:',f.name
					l_count = 0
			pass
		except Exception as e:
			if not ( e.args[1].endswith("doesn't exist") and e.args[1].startswith("Table") ):
				print e
			pass

	f.close()
	
	print 'completed'

cursor.close()  
conn.close()

print 'records num =',r_counter

