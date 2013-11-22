import os

import common.lib as lib
import common.config as config

class ToFileQuery(object):
    class DirException(Exception): pass

    def __init__(self):
        self.__sql = "select * from tbname where CUID = 1"
        self.__max_cuid = 0
        self.__open_dir()
        self.__open_file()

    def __open_dir(self):
        self.output_dir = lib.new_output_dir()
        if self.output_dir == "":
            raise DirException, "Cannot create output dir"
        self.f_num = 1

    def __open_file(self):
        self.l_num = 0
        self.f = open(str(self.f_num) + '.txt', 'w')
        print 'new file:',self.f.name

    def __close_file(self):
        self.f.close()

    def get_sql(self):
        return self.__sql

    def process(self, row):
        for field in row:
            self.f.write(str(int(field)) + ', ')
        self.f.write(os.linesep)
        self.l_num += 1
        if self.l_num >= config.query_output_lines:
            self.__close_file()
            self.f_num += 1
            self.__open_file()
	
    def __str__(self):
        return "file num %s" % self.f_num

    def __del__(self):
        self.__close_file()

if __name__ == "__main__":
    import query
    query.query(ToFileQuery())

