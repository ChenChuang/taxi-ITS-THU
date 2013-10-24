library(RPostgreSQL)

write.ways <- function(df, tbname="ways_used_times_test") {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po", user="postgres")

    dbWriteTable(conn, tbname, df)
}
