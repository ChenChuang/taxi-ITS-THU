library(RPostgreSQL)

rank.avg.between <- function(a, b) {    
    drv <- dbDriver("PostgreSQL")
    conn <- dbConnect(drv, dbname="beijing_taxi", user="postgres")
    sql <- paste("select", 
                 "avg(bn) as abn,", 
                 "avg(st) as ast,",
                 "avg(iv) as aiv,",
                 "avg(uti) as auti",
                 "from taxi_paths_compare as taxi_paths_compare, taxi_tracks_attr",
                 "where taxi_paths_compare.tid = taxi_tracks_attr.tid",
                 "and bn*st*iv*uti > 0",
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
                 stddev(bn) as vbn, 
                 stddev(st) as vst,
                 stddev(iv) as viv,
                 stddev(uti) as vuti 
                 from taxi_paths_compare as taxi_paths_compare, taxi_tracks_attr 
                 where taxi_paths_compare.tid = taxi_tracks_attr.tid 
                 and bn*st*iv*uti > 0 
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

    df <- df[df$bn * df$st * df$iv * df$ut * df$uti > 0, c('bn','st','iv','uti')]
    return(df)
}

hist.ranks.together <- function(df) {
    methods <- c('bn','st','iv','uti')
    legends <- c('Shortest path', 'ST-Matching', 'IVVM', 'FM-Matching')
    ma <- NULL
    for(method in methods) {
        ranks <- hist(df[[method]], breaks=seq(from=0.5, to=5.5, by=1.0), plot=F)
        if(is.null(ma)) {
            ma <- ranks$counts
        }else {
            ma <- rbind(ma, ranks$counts)
        }
    }
    # cols <- c(51,125,132,'red')
    cols <- c('chartreuse4','blue','darkorchid','red')
    barplot(ma, beside=T, ylim=c(0,400), col=cols, xlab='Rank', ylab='Frequency', cex.lab=1.5, cex.axis=1.5) 
    legend('topleft', legend=legends, fill=cols, border=F, bty="n", cex=1.5)
    axis(1, at=seq(from=3,by=5,length.out=5), labels=c('1','2','3','4','5'), las=1, cex.axis=1.5)
    box(bty = "o")
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

read.sample.attr <- function(filename='sample_maxd.txt') {
    # filename <- 'sample_maxd.txt'
    # filename <- 'sample_avgd.txt'
    df <- read.table(filename,
                     header=T, dec='.', sep=',', quot='\n')
    return(df)
}

hist.sample.len <- function(df) {

}

hist.sample.avgd <- function(df) {
    legends <- c('benchmark','down-sampling-rate = 2', 'down-sampling-rate = 4', 'down-sampling-rate = 6', 'down-sampling-rate = 8')
    ma <- NULL
    breaks <- seq(from=0.0, to=2.2, by=0.2)
    for(i in seq(2, ncol(df))) {
        h <- hist(df[,i], breaks=breaks, plot=F)
        if(is.null(ma)) {
            ma <- h$counts
        }else {
            ma <- rbind(ma, h$counts)
        }
    }
    cols <- c('grey','chartreuse4','blue','darkorchid','red')
    barplot(ma, beside=F, xlim=c(0,13.3), ylim=c(0,35), col=cols, xlab='Sample Interval [km]', ylab='Number of Trajectories', cex.lab=1.5, cex.axis=1.5) 
    legend('topright', legend=legends, fill=cols, border=F, bty="n", cex=1.5)
    axis(1, at=seq(from=0.1,by=1.2,length.out=12), labels=as.character(breaks), las=1, cex.axis=1.5)
    box(bty = "o")
}

hist.sample.maxd <- function(df) {
    legends <- c('Sample interval = 2', 'Sample interval = 4', 'Sample interval = 6', 'Sample interval = 8')
    ma <- NULL
    for(i in seq(2, ncol(df))) {
        h <- hist(df[,i], breaks=seq(from=0.0, to=5.5, by=0.5), plot=F)
        if(is.null(ma)) {
            ma <- h$counts
        }else {
            ma <- rbind(ma, h$counts)
        }
    }
    cols <- c('chartreuse4','blue','darkorchid','red')
    barplot(ma, beside=F, ylim=c(0,25), col=cols, xlab='Max Interval [km]', ylab='Number', cex.lab=1.5, cex.axis=1.5) 
    legend('topright', legend=legends, fill=cols, border=F, bty="n", cex=1.5)
    axis(1, at=seq(from=0.1,by=2.4,length.out=6), labels=c('0','1','2','3','4','5'), las=1, cex.axis=1.5)
    box(bty = "o")
}
hist.interval <- function(df) {
    hist(df$interval, breaks=25, xlab='Average interval [km]', main='')
}

hist.max_d <- function(df) {
    ah <- hist(df$max_d, breaks=50, plot=F)
    i <- ah$breaks[2]-ah$breaks[1]
    barplot(ah$counts, col=('white'), beside=F, space=0, cex.lab=1.5, cex.axis=1.5, xlim=c(0,12)/i, ylim=c(0,70), ylab='Number of trajectories', xlab='Max interval [km]')
    axis(1, at=seq(from=0,to=12/i,by=2/i), labels=c('0','2','4','6','8','10','12'), las=1, cex.axis=1.5)
    box(bty = "o")
}

hist.length <- function(df) {
    hist(df$length, breaks=25, xlab='Length [km]', main='')
}

read.ranks.avg <- function() {
    dff <- read.compare.tracks()
    s <- unname(quantile(dff$max_d,  probs = c(0,25,50,75,100)/100))

    # s <- c(0, 0.5, 1.0, 2.0, 4.0, 1000000)
    print(s)

    df <- data.frame()
    for(i in 1:(length(s)-1)) {
        rs <- rank.avg.between(s[i], s[i+1])
        df <- rbind(df, rs)
    }
    return(df)
}

read.ranks.var <- function() {
    dff <- read.compare.tracks()
    s <- unname(quantile(dff$max_d,  probs = c(0,25,50,75,100)/100))

    # s <- c(0, 0.5, 1.0, 2.0, 4.0, 1000000)
    print(s)

    df <- data.frame()
    for(i in 1:(length(s)-1)) {
        rs <- rank.var.between(s[i], s[i+1])
        df <- rbind(df, rs)
    }
    return(df)
}

plot.ranks.avg <- function(df) {
    yrange <- c(3.5,5.0)
    xrange <- c(0.7,4.3)
    n <- length(df$abn)
    # x11()
    plot(xrange, yrange, type="n", xaxt="n", xlab="Max interval [km]", ylab="Average of ranks", cex.lab=1.5, cex.axis=1.5) 
    linetype <- c(6,2,1,4) 
    plotchar <- c(0, 1, 2, 15)
    cols <- c('chartreuse4','blue','darkorchid','red')
    text <- c('Shortest path','ST-Matching','IVVM','FM-Matching')
    for(i in 1:4) {
        lines(1:n, df[[i]], type="b", col=cols[i], lwd=2, lty=linetype[i], pch=plotchar[i])
    }
    axis(1, at=c(0.7,1.5,2.5,3.5,4.3), labels=c('0.00','0.81','1.27','2.43','11.45'), las=1, cex.axis=1.5)
    legend(xrange[1], yrange[2]+0.05, col=cols, legend=text, pch=plotchar, lty=linetype, lwd=2, bty="n", cex=1.5)
}

plot.ranks.var <- function(df) {
    yrange <- c(0.75,1.5)
    xrange <- c(0.7,4.3)
    n <- length(df$vbn)
    # x11()
    plot(xrange, yrange, type="n", xaxt="n", xlab="Max interval [km]", ylab="Standard deviation of ranks", cex.lab=1.5, cex.axis=1.5) 
    linetype <- c(6,2,1,4) 
    plotchar <- c(0, 1, 2, 15)
    cols <- c('chartreuse4','blue','darkorchid','red')
    text <- c('Shortest path','ST-Matching','IVVM','FM-Matching')
    for(i in 1:4) {
        lines(1:n, df[[i]], type="b", col=cols[i], lwd=2, lty=linetype[i], pch=plotchar[i])
    }
    axis(1, at=c(0.7,1.5,2.5,3.5,4.3), labels=c('0.00','0.81','1.27','2.43','11.45'), las=1, cex.axis=1.5)
    legend(xrange[2]-1.5, yrange[2]+0.02, col=cols, legend=text, pch=plotchar, lty=linetype, lwd=2, bty="n", cex=1.5)
}

read.precisions <- function() {
    # filename <- 'sample_gt_1.txt'
    filename <- 'sample_compare_result.txt'
    df <- read.table(filename,
                     header=F, dec='.', col.names=c('method','sample','matched','missed','false'))
    return(df)
}

read.precisions.maxd <- function() {
    # filename <- 'sample_gt_1.txt'
    filename <- 'sample_result_4.txt'
    df <- read.table(filename,
                     header=F, dec='.', col.names=c('method','maxda','maxdb','matched','missed','false'))
    return(df)
}

plot.column <- function(df, col, yrange) {
    xrange <- c(1.8,8.2)
    # x11()
    require(Hmisc)
    if(col == "matched") {
        ylab <- "Correct Length Propotion"
    }
    if(col == "missed") {
        ylab <- "Missed Length Propotion"
    }
    if(col == "false") {
        ylab <- "False Length Propotion"
    }
    plot(xrange, yrange, xaxt="n", type="n", xlab="Down-Sampling-rate", ylab = ylab, cex.lab=1.5, cex.axis=1.5) 
    linetype <- c(6,2,1,4) 
    plotchar <- c(0, 1, 2, 15)
    cols <- c('chartreuse4','blue','darkorchid','red')
    text <- c('bn','st','iv','uti')
    legends <- c('HMM','ST-Matching','IVVM','SF-Matching')
    for(i in 1:4) {
        s = df[df$method == text[i], 'matched'] + df[df$method == text[i], 'missed']
        lines(c(2,4,6,8), df[df$method == text[i], col]/s, type="b", lwd=2, col=cols[i], lty=linetype[i], pch=plotchar[i], xaxt='n', ann=F)
    }
    if(col == 'matched') {
        legendx = xrange[2] - 2.7
    }else{
        legendx = xrange[1]
    }
    axis(1, at=c(2,4,6,8), labels=c('2','4','6','8'), las=1, cex.axis=1.5)
    legend(legendx, yrange[2]+0.007, legend=legends, col=cols, pch=plotchar, lty=linetype, lwd=2, bty="n", cex=1.5)
}

plot.column.maxd <- function(df, col, yrange) {
    xrange <- c(0,6)
    # x11()
    require(Hmisc)
    plot(xrange, yrange, xaxt="n", type="n", xlab="Maxd", ylab = capitalize(paste(col,"ratio")), cex.lab=1.5, cex.axis=1.5) 
    linetype <- c(6,2,1,4) 
    plotchar <- c(0, 1, 2, 15)
    cols <- c('chartreuse4','blue','darkorchid','red')
    text <- c('bn','st','iv','uti')
    legends <- c('HMM','ST-Matching','IVVM','SF-Matching')
    for(i in 1:4) {
        s = df[df$method == text[i], 'matched'][2:12] + df[df$method == text[i], 'missed'][2:12] + 1
        lines(seq(from=0.75, by=0.5, length.out=11), df[df$method == text[i], col][2:12]/s, type="b", lwd=2, col=cols[i], lty=linetype[i], pch=plotchar[i], xaxt='n', ann=F)
    }
    if(col == 'matched') {
        legendx = xrange[2] - 2.7
    }else{
        legendx = xrange[1]
    }
    # axis(1, at=c(2,4,6,8), labels=c('2','4','6','8'), las=1, cex.axis=1.5)
    legend(legendx, yrange[2]+0.007, legend=legends, col=cols, pch=plotchar, lty=linetype, lwd=2, bty="n", cex=1.5)
}
plot.matched <- function(df) {
    plot.column(df, 'matched', c(0.75,1.0))
}

plot.missed <- function(df) {
    plot.column(df, 'missed', c(0.02,0.25))
}

plot.false <- function(df) {
    plot.column(df, 'false', c(0.02,0.20))
}

if(F) {
    # source("compare_mm.r")

    setEPS()

    postscript("../../../paper/hist-ranks.eps", width=6, height=5)
    df <- read.ranks()
    # hist.ranks(df,'bn')
    hist.ranks.together(df)
    dev.off()

    postscript("../../../paper/ranks-avg.eps")
    df <- read.ranks.avg()
    plot.ranks.avg(df)
    dev.off()

    postscript("../../../paper/ranks-stddev.eps")
    df <- read.ranks.var()
    plot.ranks.var(df)
    dev.off()

    postscript("../../../paper/matched.eps")
    df <- read.precisions()
    plot.matched(df)
    dev.off()

    postscript("../../../paper/missed.eps")
    plot.missed(df)
    dev.off()

    postscript("../../../paper/false.eps")
    plot.false(df)
    dev.off()

    postscript("../../../paper/hist-maxd.eps", width=6, height=5)
    df <- read.compare.tracks()
    hist.max_d(df)
    dev.off()

    postscript("../../../paper/hist-sample-avgd.eps")
    df <- read.sample.attr(filename <- 'sample_avgd.txt') 
    hist.sample.avgd(df)
    dev.off()

    postscript("../../../paper/hist-sample-len.eps")
    df <- read.sample.attr(filename <- 'sample_len.txt') 
    hist.sample.len(df)
    dev.off()
}
