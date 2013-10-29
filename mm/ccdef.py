try:
    INF = float('inf')
except:
    INF = 1e7

class Summary(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def printme(self):
        print "summary:",
        for k,v in self.__dict__.iteritems():
            print str(k),"=",str(v),
