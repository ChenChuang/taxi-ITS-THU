import compute as com
dirname = 'mat2/'
com.create_var_from_db(dirname)
[amat, bmat, x0, info] = com.create_Ab_from_db(3400, 49122, 3, True, dirname)
