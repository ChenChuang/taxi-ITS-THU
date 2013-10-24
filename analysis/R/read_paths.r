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
    #sql <- "select tid, way_ids as ways, length from taxi_paths_dp limit 2"
	#sql <- "select taxi_paths.tid as tid, way_ids as ways from taxi_paths,taxi_paths_attr where taxi_paths.tid=taxi_paths_attr.tid and taxi_paths_attr.valid=1"    
	max_tid = 100000
    sql <- paste("select taxi_paths_bn.tid as tid, way_ids as ways, length, conf from taxi_paths_bn,taxi_paths_bn_attr where taxi_paths_bn.tid=taxi_paths_bn_attr.tid and taxi_paths_bn.tid <=",max_tid)
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
