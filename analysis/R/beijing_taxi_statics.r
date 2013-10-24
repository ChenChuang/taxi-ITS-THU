library(DBI)
library(RMySQL)
drv <- dbDriver("MySQL")
ch <- dbConnect(drv,dbname="db_beijing_taxi","root","123456")
alltablenames <- dbGetQuery(ch, "show tables")
validtablenames <- grep("^tb_\\d{8}$",alltablenames[[1]],value=T)
alldata = list()
i=1
for(tablename in validtablenames) {
    cat("Querying",tablename,"...")
    alldata[[i]] = dbGetQuery(ch, paste("select * from ", tablename, sep=""))
	i=i+1
    cat("done\n")
}
