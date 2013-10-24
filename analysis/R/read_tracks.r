library(xts)
library(RPostgreSQL)

new.track <- function(r) {
    print(r$tid)
    flush.console()
    
    track <- list()
    track$tid <- r$tid
    track$cuid <- r$cuid
    
    rds <- data.frame(time = numeric(0), 
                      lon = numeric(0),
                      lat = numeric(0),
                      head = numeric(0),
                      speed = numeric(0))

    geom <- substr(r$geom, 12, nchar(r$geom)-1)
    desc <- substr(r$desc, 1, nchar(r$desc)-1)
    
    lonlatstrs <- strsplit(geom, ",")[[1]]
    thsostrs <- strsplit(desc, ",")[[1]]
    
    rdslen <- length(lonlatstrs)
    for(i in 1:length(lonlatstrs)){
        lonlatstr <- lonlatstrs[i]
        lonlats <- strsplit(lonlatstr, " ")[[1]]
        lon <- as.numeric(lonlats[1])
        lat <- as.numeric(lonlats[2])

        thsostr <- thsostrs[i]
        thsos <- strsplit(thsostr, " ")[[1]]

        t <- as.POSIXct(thsos[1], format="%Y-%m-%dT%H:%M:%SZ", origin="1970-01-01", tz="UTC")
        h <- as.numeric(thsos[2])
        s <- as.numeric(thsos[3])
        o <- as.numeric(thsos[4])
        
        rds <- rbind(rds, c(t,lon,lat,h,s))
    }
 
    names(rds) <- c('time','lon','lat','head','speed') 
    rds$time <- as.POSIXlt(rds$time, origin="1970-01-01", tz="UTC") 
    track$rds <- xts(rds[,-1], order.by=rds[,1])
    
    return(track)
}

read.tracks <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- "select id as tid, cuid, st_astext(track_geom) as geom, track_desc as desc from taxi_tracks limit 2;"
    rs <- dbSendQuery(conn, sql)

    all.tracks <- list()
    r <- fetch(rs, 1)
    while(length(r) > 0) {
        tryCatch( {
            track <- new.track(r)
        }, error = function(e) {
            print(paste("E:",r$tid))
            track <- NULL
        } )
        if(!is.null(t)) {
            all.tracks[[length(all.tracks)+1]] <- track
        }
        r <- fetch(rs, 1)
    }
    
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    return(all.tracks)
}


