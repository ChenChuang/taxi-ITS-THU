def func(fri, toi, i):
    import compute as com
    com.create_var_from_db()
    [amat, bmat, x0mat, info] = com.create_Ab_from_db(fri, toi, i)
    return [amat, bmat, x0mat, info]

def functest(fri, toi, i):
    for i in xrange(0,1000000):
        for j in xrange(0, 10000):
            s = fri*toi
    return [0,1,2,3]

def create_Ab_from_db_parallel():
    import datetime
    import pprocess as pp
    import compute as com
    com.create_var_from_db()
    nproc = 3
    nv_per = int(com.nv / 3)
    ress = pp.Map(limit=nproc)
    pfunc = ress.manage(pp.MakeParallel(functest))

    start_at = datetime.datetime.now() 
    
    for i in range(0,nproc):
        fri = i * nv_per
        toi = (i+1) * nv_per
        if i == nproc-1:
            toi = com.nv
        pfunc(1, 1, 1)
    ress = ress[:]
    amat  = sum([res[0] for res in ress])
    bmat  = sum([res[1] for res in ress])
    x0mat = sum([res[2] for res in ress])
    
    end_at = datetime.datetime.now()
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at - start_at
    com.write_mat(amat, 'amat.mtx')
    com.write_mat(bmat, 'bmat.mtx')
    com.write_mat(x0mat, 'x0mat.mtx')

    info = {'nnz': amat.nnz, 'nall':nv*nv}
    return [amat, bmat, x0mat, info]


