trajectorydir <- "/home/chenchuang/beijing_taxi_proc_output/occupied"
validdirnames <- list.dirs(path = trajectorydir, full.names = T, recursive = F)

alldata <- list()
i <- 1
for(dirname in validdirnames) {
    cuid <- tail(strsplit(dirname,"_")[[1]], 1)
    cat("CUID:", cuid, "...")
    tmplist <- list()
    validfilenames <- list.files(path = paste(dirname,"/data",sep = ""), full.names = T)
    for(filename in validfilenames) {
        #cat("Reading",filename,"...")
        cat("...")
        tmplist <- rbind(tmplist, read.table(filename, header=F, sep=", ", col.names=c("CUID","TIMESTAMP","LAT","LON","HEAD","SPEAD","HEAVY")))
        #cat("done\n")
    }
    alldata[[i]] <- tmplist
    i <- i+1
    cat("done\n")
}


