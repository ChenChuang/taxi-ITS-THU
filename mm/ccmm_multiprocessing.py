from multiprocessing import Pool
import datetime
import ccmm_ways_attr_worker as worker

if __name__ == "__main__":
    core_num = 3
    tids = [5000, 5050, 5100, 5150]

    start_at = datetime.datetime.now()
    print ('using total ' + str(core_num) + ' cores' + ' start at ' + str(start_at) + ' ').center(70, '-')

    pool = Pool(processes = core_num)

    params = []
    for i in range(core_num):
        params.append((i+1, tids[i], tids[i+1]-1))
    results = pool.map(worker.mm, params)

    end_at = datetime.datetime.now() 
    print ('using total ' + str(core_num) + ' cores' + ' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)


