library(RPostgreSQL)

read.ways.attr <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_mm_po", user="postgres")

    df <- dbReadTable(conn, "ways_ut_attr")

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    return(df)
}

# ways.attr <- read.ways.attr()

used_times.valid <- ways.attr[ways.attr$used_times > 0,]
used_times.hist <- hist(used_times.valid$used_times, breaks=500, plot=F)
used_times.hist$counts[used_times.hist$counts == 0] <- 0.1
# used_times.hist$counts <- log(used_times.hist$counts + 1, 10)
plot(used_times.hist$counts, log="y", type='h', lwd=10, lend=2 )

used_times.sorted <- used_times.valid[order(used_times.valid$used_times),]
used_times.sorted$used_times <- log(used_times.sorted$used_times)
plot(used_times.sorted$used_times,  type='h')
