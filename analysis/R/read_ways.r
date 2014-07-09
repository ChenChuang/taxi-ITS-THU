library(RPostgreSQL)

read.ways <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    df <- dbReadTable(conn, "ways")

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    df.ways = df[c("id","source","target","km","kmh")]
    return(df.ways)
}

read.ways.attrs <- function(columns) {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    # df <- dbReadTable(conn, "ways_and_attrs_2")
    df <- dbReadTable(conn, "ways_and_pickdrop")

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    df.ways.attrs = df[columns]
    return(df.ways.attrs)   
}

read.ways.attrs.by.hour <- function(hour, columns) {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    df <- dbReadTable(conn, paste0("ways_and_attrs_h", sprintf('%02d',hour)))

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    df.ways.attrs = df[columns]
    return(df.ways.attrs)
}



read.som.clust <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    rs <- dbGetQuery(conn,"select distinct(clust, cat) from ways_clust_som_3 order by (clust,cat);")
    
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    rs <- rs[[1]]
    return(rs)
}

read.ways.cato <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    rs <- dbGetQuery(conn,"select cat from ways_clust_som_3 order by wid;")
    
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    rs <- rs[[1]]
    return(rs)
}
