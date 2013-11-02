library(RPostgreSQL)

rank.between <- function(a, b) {    
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- paste("select 
                 avg(bn) as abn, 
                 avg(st) as ast,
                 avg(iv) as aiv,
                 avg(ut) as aut,
                 avg(uti) as auti 
                 from taxi_paths_compare,taxi_tracks_attr 
                 where taxi_paths_compare.tid = taxi_tracks_attr.tid 
                 and bn*st*iv*ut*uti > 0 
                 and length/rds_num >", a, "and length/rds_num <=", b, "and taxi_tracks_attr.tid <= 1000")
    rs <- dbGetQuery(conn, sql)
    dbDisconnect(conn)
    dbUnloadDriver(drv) 
    return(rs)
}

read.compare.tracks <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- "select tid,length,rds_num from taxi_tracks_attr where tid in (select tid from taxi_paths_compare)"
    rs <- dbGetQuery(conn, sql)
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    rs$interval <- rs$length / rs$rds_num
    return(rs)
}

hist.interval <- function(df) {
    hist(rs$interval, breaks=25)
}

compare.rank <- function() {
    s <- c(0, 0.2, 0.4, 0.6, 2.0, 1000000)
    df <- data.frame()
    for(i in 1:(length(s)-1)) {
        rs <- rank.between(s[i], s[i+1])
        df <- rbind(df, rs)
    }
    return(df)
}

plot.rank <- function(df) {
    yrange <- c(3.0,4.5)
    xrange <- c(0.7,5.3)
    x11()
    plot(xrange, yrange, type="n", xaxt="n", xlab="Sampling rate", ylab="Rank") 
    linetype <- c(1:5) 
    plotchar <- c(1, 2, 0, 17, 15)
    text <- c('bn','st','iv','ut','uti')
    for(i in 1:5) {
        lines(1:5, df[[i]], type="b", lwd=1, lty=linetype[i], pch=plotchar[i])
    }
    axis(1, at=1:5, labels=c('Very High','High','Medium','Low','Very Low'), las=1)
    legend(xrange[1], yrange[2], legend=text, pch=plotchar, lty=linetype, bty="n")
}

read.precision <- function() {
    df <- read.table('sample_compare_result.txt',
                     header=F, dec='.', col.names=c('method','sample','matched','missed','false'))
    return(df)
}

plot.column <- function(df, col, yrange) {
    xrange <- c(1.8,8.2)
    x11()
    require(Hmisc)
    plot(xrange, yrange, type="n", xlab="Sampling interval", ylab = capitalize(paste(col,"precision"))) 
    linetype <- c(1:5) 
    plotchar <- c(1, 2, 0, 17, 15)
    text <- c('bn','st','iv','ut','uti')
    for(i in 1:5) {
        s = df[df$method == text[i], 'matched'] + df[df$method == text[i], 'missed']
        lines(c(2,4,6,8), df[df$method == text[i], col]/s, type="b", lwd=1, lty=linetype[i], pch=plotchar[i])
    }
    if(col == 'matched') {
        legendx = xrange[2] - 1
    }else{
        legendx = xrange[1]
    }
    legend(legendx, yrange[2], legend=text, pch=plotchar, lty=linetype, bty="n")
}

plot.matched <- function(df) {
    plot.column(df, 'matched', c(0.77,1.0))
}

plot.missed <- function(df) {
    plot.column(df, 'missed', c(0.02,0.22))
}

plot.false <- function(df) {
    plot.column(df, 'false', c(0.02,0.22))
}
