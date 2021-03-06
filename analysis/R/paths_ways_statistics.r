debug <- F

fontsize <- 2

# read ALL paths generated by BN from database
if(debug) {
    source('read_paths.r')
    print('reading paths')
    paths <- read.paths()
}

# read ways from database
if(debug) {
    source('read_ways.r')
    ways <- read.ways()
}

# read ways and their statistical attributes from database
if(debug) {
    source('read_ways.r')
    print('reading ways and attrs')
    df.ways.attrs <- read.ways.attrs(c('id','used_times','used_interval','km','kmh'))
}

# retrive speed sequences of all paths
if(F) {
    paths.speeds <- lapply(paths, path2speeds)
}

# plot hist of used_times of ALL ways
hist.log.ways.used_times <- function(df.ways.attrs) {
    a <- df.ways.attrs[['used_times']]
    ah <- hist(a, breaks=60, plot=F)
    ah$counts <- ah$counts + 1
    # ah$counts <- log10(ah$counts + 1)
    barplot(ah$counts, col=('white'), log='y', beside=F, space=0, cex.lab=1.5, cex.axis=1.5, ylim=c(0.1,100000), ylab='log10( Number of roads + 1 )', xlab=expression(italic('f'['r'])))
    axis(1, at=seq(from=0,to=64,length.out=5), labels=c('0','1600','3200','4800','6400'), las=1, pos=0.055, cex.axis=1.5)
    box(bty = "o")
    # rect(xleft=-1, ybottom=0.055, xright=6500, ytop=100000)
}

# plot hist of used_times of ALL ways
hist.log.rough.ways.used_times <- function(df.ways.attrs) {
    a <- df.ways.attrs[['used_times']]
    ah <- hist(a, breaks=12, plot=F)
    ah$counts <- ah$counts + 1
    # ah$counts <- log10(ah$counts + 1)
    barplot(ah$counts, , log='y', beside=F, space=0, cex.lab=fontsize, cex.axis=fontsize, ylim=c(0.1,1000000), ylab='log10( Number of roads + 1 )', xlab=expression(italic('f'['r'])))
    axis(1, at=seq(from=0,by=1,length.out=length(ah$breaks)), labels=as.character(ah$breaks), las=1, cex.axis=fontsize)
    box(bty = "o")
    # rect(xleft=-1, ybottom=0.055, xright=6500, ytop=100000)
}

# plot hist of used_times of ALL ways
hist.ways.used_times <- function(df.ways.attrs) {
    a <- df.ways.attrs[['used_times']]
    ah <- hist(a[a>300], breaks=25, plot=F)
    n <- length(ah$breaks)
    barplot(ah$counts, col=('white'), beside=F, space=0, cex.lab=1.5, cex.axis=1.5, ylim=c(0,3200), ylab='Number of roads', xlab=expression(italic('f'['r'])))
    axis(1, at=seq(from=0,to=n,length.out=5), labels=c('0','1600','3200','4800','6400'), las=1, pos=0.055, cex.axis=1.5)
    box(bty = "o")
    # rect(xleft=-1, ybottom=0.055, xright=6500, ytop=100000)
}

# plot hist of kmh of ALL ways
hist.ways.kmh <- function(df.ways.attrs) {
    a <- df.ways.attrs[['kmh']]
    ah <- hist(a, breaks=12, plot=F)
    barplot(ah$counts, col=('white'), beside=F, space=0, cex.lab=1.5, cex.axis=1.5, cex=1.5, ylim=c(0,19000), names.arg=seq(from=10,by=10,length.out=12), ylab='Number of roads', xlab='Speed Limit [km/h]')
    box(bty = "o")
}

# statistical attribute sequence of ways in pathi, slow and deprecated
path2wayattrs <- function(p, attr) {
    ws <- p$ways
    ss <- rep(-1,length(ws))
    for(i in seq(ws)) {
        ss[i] <- df.ways.attrs[df.ways.attrs$id == ws[i], attr]
    }
    return(ss)
}

if(debug) {
    ways.num <- length(df.ways.attrs$id)

    print('generating ways.used_times')    
    ways.used_times <- rep(0, ways.num)
    for(i in 1:ways.num) {
        ways.used_times[i] <- df.ways.attrs[df.ways.attrs$id == i, 'used_times']
    }

    print('generating ways.used_interval.text')    
    ways.used_interval.text <- rep(0, ways.num)
    for(i in 1:ways.num) {
        ways.used_interval.text[i] <- df.ways.attrs[df.ways.attrs$id == i, 'used_interval']
    }

    print('generating ways.used_interval')    
    ways.used_interval <- list(rep(0, ways.num))
    for(i in 1:ways.num) {
        ways.used_interval[[i]] <- unlist(lapply(strsplit(df.ways.attrs[df.ways.attrs$id == i, 'used_interval'], ','), as.numeric))
    }

    print('generating ways.km')    
    ways.km <- rep(0, ways.num)
    for(i in 1:ways.num) {
        ways.km[i] <- df.ways.attrs[df.ways.attrs$id == i, 'km']
    }

    print('generating ways.kmh')    
    ways.kmh <- rep(0, ways.num)
    for(i in 1:ways.num) {
        ways.kmh[i] <- df.ways.attrs[df.ways.attrs$id == i, 'kmh']
    }
}

read.ways.used_interval <- function() {
    df.ways.attrs <- read.ways.attrs(c('id','used_times','used_interval','km','kmh'))
    ways.num <- length(df.ways.attrs$id)
    ways.used_interval <- list(rep(0, ways.num))
    for(i in 1:ways.num) {
        ways.used_interval[[i]] <- unlist(lapply(strsplit(df.ways.attrs[df.ways.attrs$id == i, 'used_interval'], ','), as.numeric))
    }
    return(ways.used_interval)
}

plot.way.used_interval <- function(i, ylim) {
    last <- ways.used_interval[[i]][10]
    plot(seq(from=0,to=1.0,by=0.1), c(ways.used_interval[[i]], last), 
         xlim=c(0,1), ylim = ylim, type = 's', xlab='Normalized Traveled Length i', ylab='SF-Feature[i]', cex.lab=fontsize, cex.axis=fontsize)
    points(x=seq(from=0.05,to=0.95,by=0.1), y=ways.used_interval[[i]], type = "p")
}

path2way.km <- function(p) {
    return(c(ways.km[p$ways]))
}

path2way.used_times <- function(p) {
    return(c(ways.used_times[p$ways]))
}

path2way.kmh <- function(p) {
    return(c(ways.kmh[p$ways]))
}

# retrive used_times sequences of all paths
if(debug) {
    print('calculating used_times sequences')
    # paths.used_timeses <- lapply(paths, path2wayattrs, attr="used_times")
    paths.used_timeses <- lapply(paths, path2way.used_times)
}

# retrive length sequences of all paths
if(debug) {
    print('calculating length sequences')
    # paths.lengths <- lapply(paths, path2wayattrs, attr="km")
    paths.lengths <- lapply(paths, path2way.km)
}

# retrive speed sequences of all paths
if(debug) {
    paths.speeds <- lapply(paths, path2way.kmh)
}

# little functions for generating used_times model of all paths
path2cumlengths <- function(pl) {
    return(c(0, cumsum(pl)))
}

path2normlengths <- function(pl) {
    sl = sum(pl)
    return(pl/sl)
}

path2usedtimes.forplot <- function(pu) {
    return(c(pu, pu[length(pu)]))
}

# generate used_times model of all paths
if(debug) {
    print('generating used_times models of all paths')    
    paths.norm.lengths <- lapply(paths.lengths, path2normlengths)
    paths.cum.lengths <- lapply(paths.lengths, path2cumlengths)
    paths.cum.norm.lengths <- lapply(paths.norm.lengths, path2cumlengths)
    paths.used_timeses.forplot <- lapply(paths.used_timeses, path2usedtimes.forplot)
}

# plot the used_times model of path with tid = i
plot.path.used_times <- function(i) {
    # print(paths[[i]]$tid)
    tmp_cls <- paths.cum.lengths[[i]]
    tmp_cnls <- paths.cum.norm.lengths[[i]]
    tmp_uts <- paths.used_timeses.forplot[[i]]
    plot(tmp_cnls, tmp_uts, type='s', xlab='Normalized Traveled Length', ylab='F-Feature') 
}

# sample the used_times model of path
sp <- 0.001
sn <- 1000
from <- 0

sample.stairs <- function(x,y,sp,sn,from) {
    max_x <- max(x)
    if(sn < 0) {
        sn <- ceiling(max_x / sp)
    }
    sx <- from
    cxi <- 1
    cx <- x[cxi]
    cy <- 0
    s <- rep(0, sn)
    si <- 0
    repeat {
        while(sx < cx) {
            si <- si + 1
            s[si] <- cy
            if(si >= sn) {
                break
            }
            sx <- sx + sp            
        }
        if(si >= sn) {
            break
        }
        cxi <- cxi + 1
        if(cxi > length(x)) {
            break
        }
        cx <- x[cxi]
        cy <- y[cxi-1]
    }
    return(s)
}

# calculate the average used_times model of all paths
avg.path.ut <- function(paths.num = -1) {
    print('calculating average used_times model from all paths')    
    if(paths.num < 0) {
        paths.num <- length(paths)
    }
    avg.uts <- rep(0, sn)
    for(i in 1:paths.num) {
        avg.uts <- avg.uts + sample.stairs(paths.cum.norm.lengths[[i]], paths.used_timeses.forplot[[i]], sp, sn, from)
    }
    return(avg.uts / paths.num)
}
i
# plot the average used_times model
plot.avg.uts <- function(avg.uts) {
    plot(seq(sp,sp*sn,sp), avg.uts, type='l', xlab='Normalized Traveled Length', ylab='F-Feature')
}

plot.multi.avg.uts <- function(ns) {
    plot(x=c(0,1), y=c(600,1650), type='n', xlab='Normalized Traveled Length', ylab='F-Feature')
    for(n in ns) {
        avg.uts <- avg.path.ut(n)
        lines(seq(sp,sp*sn,sp), avg.uts, type='l')
    }
}

if(F) {
    avg.uts <- avg.path.ut()
    plot.avg.uts(avg.uts)
}


if(T) {
    # source('paths_ways_statistics.r')
    # source('read_ways.r')
    # ways.used_interval <- read.ways.used_interval()

    setEPS()
    
    postscript("../../../paper/dpm/way1.eps")
    par(pin=c(6,6))
    plot.way.used_interval(1136, c(0,400))
    dev.off()
    
    postscript("../../../paper/dpm/way2.eps")
    par(pin=c(6,6))
    plot.way.used_interval(1872, c(0,800))
    dev.off()

    df.ways.attrs <- read.ways.attrs(c('id','used_times','used_interval','km','kmh'))
    postscript("../../../paper/dpm/hist-log-rough-fm.eps")
    par(pin=c(6,6))
    hist.log.rough.ways.used_times(df.ways.attrs)
    dev.off()
}










