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

    df <- dbReadTable(conn, "ways_and_attrs")

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    df.ways.attrs = df[columns]
    return(df.ways.attrs)   
}
