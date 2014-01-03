library(RPostgreSQL)

rank.avg.between <- function(a, b) {    
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- paste("select", 
                 "avg(bn) as abn,", 
                 "avg(st) as ast,",
                 "avg(iv) as aiv,",
                 "avg(ut) as aut,",
                 "avg(uti) as auti",
                 "from taxi_paths_compare as taxi_paths_compare, taxi_tracks_attr",
                 "where taxi_paths_compare.tid = taxi_tracks_attr.tid",
                 "and bn*st*iv*ut*uti > 0",
                 "and max_d >", a, "and max_d <=", b, "and taxi_tracks_attr.tid <= 1000")
    rs <- dbGetQuery(conn, sql)
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    return(rs)
}

rank.var.between <- function(a, b) {    
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- paste("select 
                 sqrt(avg(bn*bn) - avg(bn)*avg(bn)) as vbn, 
                 sqrt(avg(st*st) - avg(st)*avg(st)) as vst,
                 sqrt(avg(iv*iv) - avg(iv)*avg(iv)) as viv,
                 sqrt(avg(ut*ut) - avg(ut)*avg(ut)) as vut,
                 sqrt(avg(uti*uti) - avg(uti)*avg(uti)) as vuti 
                 from taxi_paths_compare as taxi_paths_compare, taxi_tracks_attr 
                 where taxi_paths_compare.tid = taxi_tracks_attr.tid 
                 and bn*st*iv*ut*uti > 0 
                 and max_d >", a, "and max_d <=", b, "and taxi_tracks_attr.tid <= 1000")
    rs <- dbGetQuery(conn, sql)
    dbDisconnect(conn)
    dbUnloadDriver(drv) 
    return(rs)
}

read.ranks <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")

    # df <- dbReadTable(conn, "taxi_paths_compare")
    df <- dbReadTable(conn, "taxi_paths_compare")
    
    dbDisconnect(conn)
    dbUnloadDriver(drv)

    df <- df[df$bn * df$st * df$iv * df$ut * df$uti > 0,]
    return(df)
}

hist.ranks.together <- function(df) {
    methods <- c('bn','st','iv','ut','uti')
    ma <- NULL
    for(method in methods) {
        ranks <- hist(df[[method]], breaks=seq(from=0.5, to=5.5, by=1.0), plot=F)
        if(is.null(ma)) {
            ma <- ranks$density
        }else {
            ma <- rbind(ma, ranks$density)
        }
    }
    cols <- c(51,125,132,504,'red')
    barplot(ma, beside=T, ylim=c(0,0.7), col=cols, xlab='rank', ylab='density') 
    legend('topleft', legend=methods, fill=cols, border=F, bty="n")
    axis(1, at=seq(from=3.5,by=6,length.out=5), labels=c('1','2','3','4','5'), las=1)
}

hist.ranks <- function(df, method) {
    hist(df[[method]], breaks=5)
}

read.compare.tracks <- function() {
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- "select tid,length,rds_num,max_d from taxi_tracks_attr where tid in (select tid from taxi_paths_compare where bn*st*iv*ut*uti > 0)"
    rs <- dbGetQuery(conn, sql)
    dbDisconnect(conn)
    dbUnloadDriver(drv)
    rs$interval <- rs$length / rs$rds_num
    return(rs)
}

hist.interval <- function(df) {
    hist(df$interval, breaks=25)
}

hist.max_d <- function(df) {
    hist(df$max_d, breaks=25)
}

read.ranks.avg <- function() {
    s <- c(0, 0.2, 0.4, 0.6, 2.0, 1000000)
    df <- data.frame()
    for(i in 1:(length(s)-1)) {
        rs <- rank.avg.between(s[i], s[i+1])
        df <- rbind(df, rs)
    }
    return(df)
}

read.ranks.var <- function() {
    s <- c(0, 0.2, 0.4, 0.6, 2.0, 1000000)
    df <- data.frame()
    for(i in 1:(length(s)-1)) {
        rs <- rank.var.between(s[i], s[i+1])
        df <- rbind(df, rs)
    }
    return(df)
}

plot.ranks.avg <- function(df) {
    yrange <- c(0.0,4.5)
    xrange <- c(0.7,5.3)
    # x11()
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

plot.ranks.var <- function(df) {
    yrange <- c(0.7,2.0)
    xrange <- c(0.7,5.3)
    # x11()
    plot(xrange, yrange, type="n", xaxt="n", xlab="Sampling rate", ylab="Rank") 
    linetype <- c(1:5) 
    plotchar <- c(1, 2, 0, 17, 15)
    text <- c('bn','st','iv','ut','uti')
    for(i in 1:5) {
        lines(1:5, df[[i]], type="b", lwd=1, lty=linetype[i], pch=plotchar[i])
    }
    axis(1, at=1:5, labels=c('Very High','High','Medium','Low','Very Low'), las=1)
    legend(xrange[2]-1, yrange[2], legend=text, pch=plotchar, lty=linetype, bty="n")
}

read.precisions <- function() {
    df <- read.table('sample_compare_result.txt',
                     header=F, dec='.', col.names=c('method','sample','matched','missed','false'))
    return(df)
}

plot.column <- function(df, col, yrange) {
    xrange <- c(1.8,8.2)
    # x11()
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

if(F) {
    source("compare_mm.r")

    setEPS()
    postscript("../../../paper/hist-ranks.eps")
    dev.off()

    df <- read.ranks()
    hist.ranks(df,'bn')
    hist.ranks.together(df)
    
    df <- read.ranks.avg()
    plot.ranks.avg(df)
    
    df <- read.ranks.var()
    plot.ranks.var(df)

    df <- read.precisions()
    plot.matched(df)
    plot.missed(df)
    plot.false(df)

    df <- read.compare.tracks()
    hist.max_d(df)
}
