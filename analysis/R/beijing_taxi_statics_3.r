library(xts)
Sys.setenv(TZ = "UTC")

trajectorydir <- "/home/chenchuang/beijing_taxi_proc_output/occupied"
MAXCUID <- 3

if(F) {
alldata <- list()
for(cuid in 1:MAXCUID) {
    cat("Reading CUID:", cuid, "...")
    tmp.data <- list()
    validfilenames <- list.files(path = paste(trajectorydir,"/CUID_",cuid,"/data",sep = ""), full.names = T)
    for(filename in validfilenames) {
        cat("...")
        tmp.data <- rbind(tmp.data, read.table(filename, header=F, sep=",", col.names=c("CUID","TIMESTAMP","LAT","LON","HEAD","SPEAD","HEAVY","tmp")))
    }
    tmp.data <- tmp.data[,!(names(tmp.data) %in% c("tmp"))]
    alldata[[cuid]] <- tmp.data
    cat("done\n")
}
}

if(F) {
alldata.xts <- list()
for(i in 1:length(alldata)) {
    alldata.xts[[i]] <- alldata[[i]]
    alldata.xts[[i]]$TIMESTAMP <- as.POSIXlt(alldata.xts[[i]]$TIMESTAMP, origin="1970-01-01", tz="UTC")
    alldata.xts[[i]] <- xts(alldata.xts[[i]][,-2], order.by=(alldata.xts[[i]][,2]))
}
}

if(F) {
alldata.intervals <- array()
for(i in 1:length(alldata.xts)) {
    l <- length(alldata.xts[[i]])
    tmp.heavy <- as.vector(alldata.xts[[i]]$HEAVY)
    tmp.intervals <- (time(alldata.xts[[i]])[2:l] - time(alldata.xts[[i]])[1:l-1])[intersect(which(tmp.heavy[2:l] != 0), which(tmp.heavy[1:l-1] != 0))]
    alldata.intervals <- c(alldata.intervals, tmp.intervals)
}
}


if(F) {
alldata.xts.trips <- list()
trips.num <- 0
for(i in 1:length(alldata)) {
    cat("Buiding trips CUID:", i, "...")
    tmp.heavy <- as.vector(alldata[[i]]$HEAVY)
    tmp.heavy.not <- which(tmp.heavy == 0)
    for(j in 1:(length(tmp.heavy.not)-1)) {
        ori = tmp.heavy.not[j]
        des = tmp.heavy.not[j+1]
        if(des - ori > 1) {
            des = des - 1
            ori = ori + 1
            #alldata.xts[[i]][ori:des]
            trips.num <- trips.num + 1
            alldata.xts.trips[[trips.num]] <- alldata[[i]][ori:des,]
            alldata.xts.trips[[trips.num]]$TIMESTAMP <- as.POSIXlt(alldata.xts.trips[[trips.num]]$TIMESTAMP, origin="1970-01-01", tz="UTC")
            alldata.xts.trips[[trips.num]] <- xts(alldata.xts.trips[[trips.num]][,-2], order.by=(alldata.xts.trips[[trips.num]][,2]))
            #cat(".",trips.num,".")
        }
    }
    cat("done\n")
}
}

if(F) {
trip.ori.lat <- function(x) as.vector((x$LAT))[1]
trip.ori.lon <- function(x) as.vector((x$LON))[1]
trip.ori.time <- function(x) time(x)[1]

trip.des.lat <- function(x) tail(as.vector((x$LAT)), 1)
trip.des.lon <- function(x) tail(as.vector((x$LON)), 1)
trip.des.time <- function(x) tail(time(x), 1)

trip.records.num <- function(x) length(x)
trip.time <- function(x) trip.des.time(x) - trip.ori.time(x)
}

if(T) {
trips.records.nums <- sapply(alldata.xts.trips, trip.records.num, simplify = T, USE.NAMES = T)
trips.times <- sapply(alldata.xts.trips, trip.time, simplify = T, USE.NAMES = T)

}



