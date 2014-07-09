import compute as com
dirname = ''
com.create_var_from_db(dirname)
[amat, bmat, x0, info] = com.create_Ab_from_db(3400, 49122, 3, True, dirname, alpha=0.5, beta=0.5, radius=2, weight='unif', stderr=1.0, fare='rmb')
