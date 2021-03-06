import ConfigParser

config = ConfigParser.ConfigParser() 
config.read("../common/config.ini")

mysql_hostname = config.get("mysql","hostname")
mysql_username = config.get("mysql","username")
mysql_passwd = config.get("mysql","passwd")
mysql_dbname = config.get("mysql","dbname")

dat_data_dir = config.get("data","dat_data_dir")
dat_reg = config.get("data","dat_reg")
txt_data_dir = config.get("data","txt_data_dir")
txt_reg = config.get("data","txt_reg")

query_output_lines = config.getint("query","query_output_lines")
query_output_dir = config.get("query","query_output_dir")

proc_input_dir = config.get("proc","proc_input_dir")
proc_output_lines = config.getint("proc","proc_output_lines")
proc_output_dir = config.get("proc","proc_output_dir")


