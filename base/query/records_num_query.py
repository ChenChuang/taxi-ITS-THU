class RecordsNumQuery(object):
    def __init__(self):
        self.__sql = "select count(*) from tbname"
        self.__records_num = 0
    
    def get_sql(self):
        return self.__sql

    def process(self, row):
        print row[0]
        self.__records_num += row[0]
    
    def __str__(self):
        return "total records num %s" % self.__records_num

if __name__ == "__main__":
    import query
    query.query(RecordsNumQuery())
