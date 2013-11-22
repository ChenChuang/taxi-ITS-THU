import MySQLdb
import getpass
import os

import common.lib as lib
import common.config as config

'''
    max_cuid = 8602
'''

fromdate = (2009,5,1)   #format:(year, month, day)
todate = (2009,5,30)   

fromtime = (0,0,0)  #24hour, format:(hour, minute, second)
totime = (23,59,59)  

conn = None
cursor = None

def opendb():
    global conn, cursor
    conn = MySQLdb.connect(
            host = config.mysql_hostname,
            user = config.mysql_username,
            passwd = getpass.getpass("db password: "),
            db = config.mysql_dbname)
    cursor = conn.cursor()

    print "mysql connected."

def closedb():
    cursor.close()  
    conn.close()

'''
queryer.get_sql()
queryer.process()
queryer.__str__()
'''
def query(queryer):
    tbnames = lib.dates_to_tbnames(fromdate, todate)
    utcs = lib.times_to_utcs(fromdate, todate, fromtime, totime)

    opendb()

    for tbname, utc in zip(tbnames, utcs):    
        try:
            nsql = queryer.get_sql().replace("tbname", tbname)

            print 'querying',tbname,'..',
            cursor.execute(nsql)
            rows = cursor.fetchall()
            print 'completed'

            for row in rows:
                queryer.process(row)
    
        except Exception as e:
            print e

    print queryer

    closedb()

    del queryer
