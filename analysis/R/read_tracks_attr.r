library(RPostgreSQL)

read.tracks.attr <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")

    df <- dbReadTable(conn, "taxi_tracks_attr")

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    return(df)
}

tracks.attr <- read.tracks.attr()

length.valid <- tracks.attr[tracks.attr$length < 80,]
length.valid.hist <- hist(length.valid$length, breaks=100)

rdsnum.valid <- tracks.attr[tracks.attr$rds_num < 100,]
rdsnum.valid.hist <- hist(rdsnum.valid$rds_num, breaks=100)

tracks.attr.valid <- tracks.attr[tracks.attr$length < 80 & tracks.attr$rds_num < 100 & tracks.attr$rds_num > 3,]
