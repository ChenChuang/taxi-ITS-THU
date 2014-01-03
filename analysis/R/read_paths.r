library(RPostgreSQL)

new.path <- function(r) {
    #print(r$tid)
    #flush.console()

    path <- list()
	path$tid <- r$tid
    path$len <- r$len
    path$conf <- r$conf
	
	if(!is.null(r$ways)) {
    	waystrs <- strsplit(r$ways, ",")[[1]]
    	ways <- as.numeric(waystrs)
    	path$ways <- ways
	}
	return(path)
}

read.paths <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
	
    max_tid      = 10000
    path_tb      = "taxi_paths_bn"
    path_attr_tb = "taxi_paths_bn_attr"
    
    sql <- paste("select ptb.tid as tid, way_ids as ways, length, conf from",path_tb,"as ptb,",path_attr_tb,"as patb where ptb.tid = patb.tid and ptb.tid <=",max_tid)
    rs <- dbSendQuery(conn, sql)

    all.paths <- list()
    r <- fetch(rs, 1)
    while(length(r) > 0) {
        tryCatch( {
            path <- new.path(r)
        }, error = function(e) {
            print(paste("E:",r$tid))
            path <- NULL
        } )
        if(!is.null(path)) {
            all.paths[[length(all.paths)+1]] <- path
        }
        r <- fetch(rs, 1)
    }

    dbDisconnect(conn)
    dbUnloadDriver(drv)
    return(all.paths)
}
