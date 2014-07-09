import compute as com
dirname = ''
com.create_var_from_db(dirname)
[amat, bmat, x0, info] = com.create_Ab_from_db(0, 1700, 1, True, dirname, alpha=0.5, beta=0.5, radius=2, weight='unif', stderr=1.0, fare='rmb')
