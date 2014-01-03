library(RPostgreSQL)

write.ways <- function(df, tbname) {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po_car", user="postgres")

    dbWriteTable(conn, tbname, df)
}

