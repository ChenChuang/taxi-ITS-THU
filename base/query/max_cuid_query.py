class MaxCuidQuery(object):
    def __init__(self):
        self.__sql = "select max(CUID) from tbname"
        self.__max_cuid = 0
    
    def get_sql(self):
        return self.__sql

    def process(self, row):
        print row[0]
        if int(row[0]) > self.__max_cuid:
		    self.__max_cuid = row[0]
	
    def __str__(self):
        return "max cuid %s" % self.__max_cuid

if __name__ == "__main__":
    import query
    query.query(MaxCuidQuery())
