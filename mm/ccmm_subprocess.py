import subprocess
import datetime
import sys
import time

if __name__ == "__main__":
    tids = [5000, 6000, 7000, 8000]
    core_num = len(tids) - 1

    start_at = datetime.datetime.now()
    print ('using total ' + str(core_num) + ' cores' + ' start at ' + str(start_at) + ' ').center(70, '-')

    ps = []
    for i in range(1, len(tids)):
        args = [sys.executable, "-u", "ccmm_ways_attr_subproc.py", str(i), str(tids[i-1]+1), str(tids[i])]
        p = subprocess.Popen(args)
        ps.append(p)
    
    if not (len(sys.argv) == 2 and sys.argv[1] == 'exit'):
        pre_status = [None for p in ps]
        while True:
            ps_status = [p.poll() for p in ps]
            for i,s in enumerate(ps_status):
                if s is not None and pre_status[i] is None:
                    pre_status[i] = s
                    print "core",i+1,"done"
            if all([x is not None for x in ps_status]):
                break
            time.sleep(60)

    end_at = datetime.datetime.now() 
    print ('using total ' + str(core_num) + ' cores' + ' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)


