import compute as com
dirname = 'mat2/'
com.create_var_from_db(dirname)
[amat, bmat, x0, info] = com.create_Ab_from_db(0, 1700, 1, True, dirname)
