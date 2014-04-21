import compute as com
dirname = 'mat2/'
com.create_var_from_db(dirname)
[amat, bmat, x0, info] = com.create_Ab_from_db(1700, 3400, 2, True, dirname)
