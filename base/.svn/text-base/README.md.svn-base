
1. modify config.ini to set the followings: 
   1) path of the folder which contains all your .dat files
   2) path of the folder which you want the .txt file converted from .dat file to be loaded
   3) the database name which to store the traffic data
   4) the regular pattern of your .dat file name
      tips: use the following python commands to test your regular pattern:
      >>>execfile("init.py")
      >>>import re
      >>>filename = enter your .dat file name here
      >>>re.compile(dat_reg).match(filename) != None
      if the answer is True, congratulations!
   5) the regular pattern of your .txt file name. normally, this is the same as your .dat file

2. python -u load_dat_txt.py    (load_dat_txt_24.py is used for the data without OCCUPIDED filed, 24 means that size of data struct is 24 bytes)
3. python -u load_txt_db.py
