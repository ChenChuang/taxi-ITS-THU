import ccdb as cdb

algs = ['uti','ut','iv','st','bn']

def main(): 
    db = cdb.DB()
    for row in get_rows():
        best = None
        for alg in algs:
            if row[alg] == 5:
                best = alg
                break
        if best is not None:
            print row['tid']
            insert_best(db, row['tid'], best)


def get_rows():
    db = cdb.DB()
    sql = "select * from taxi_paths_compare"
    db.cursor.execute(sql)
    while True:
        row = db.cursor.fetchone()
        if row is None:
            break 
        yield row

def insert_best(db, tid, best):
    from_tb = "taxi_paths_" + best
    to_tb = "taxi_paths_gt_rank"
    from_attr = from_tb + "_attr"
    to_attr = to_tb + "_attr"

    sql = "insert into " + to_tb + " select * from " + from_tb + " where tid=" + str(tid)
    rs = db.cursor.execute(sql)
    db.conn.commit()

    sql = "insert into " + to_attr + " select * from " + from_attr + " where tid=" + str(tid)
    rs = db.cursor.execute(sql)
    db.conn.commit()

if __name__ == "__main__":
    main()

