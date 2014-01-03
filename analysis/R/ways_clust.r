read.ways.sf <- function() {
    source('read_ways.r')

    print('reading ways and attrs')
    df.ways.attrs <- read.ways.attrs(c('id','used_times','used_interval','km','kmh'))

    print('generating ways.st')    
    ways.num <- length(df.ways.attrs$id)
    ways.sf <- list(rep(0, ways.num))
    for(i in 1:ways.num) {
        ways.sf[[i]] <- unlist(lapply(strsplit(df.ways.attrs[df.ways.attrs$id == i, 'used_interval'], ','), as.numeric))
    }

    return(ways.sf)
}

list2matrix <- function(alist) {
    ncol <- length(alist[[1]])
    output <- matrix(unlist(alist), ncol=ncol, byrow=T)
    return(output)
}

normalize.mat <- function(amat) {
    bmat <- amat
    for(i in 1:nrow(amat)) {
        amin <- min(amat[i,])
        amax <- max(amat[i,])
        am <- (amin + amax) / 2
        bmat[i,] <- (amat[i,]-amin)/(amax-amin + 1)
        # bmat[i,] <- (amat[i,]-am) / (am+1)
    }
    return(bmat)
}

filter.mat <- function(amat, amin) {
    bmat <- matrix(nrow=0, ncol=ncol(amat))
    for(i in 1:nrow(amat)) {
        amax <- max(amat[i,])
        if(amax > amin) {
            bmat <- rbind(bmat, amat[i,])
        }
    }
    return(bmat)
}

smooth.mat <- function(amat, n=3) {
    library(zoo)
    w <- ncol(amat)
    bmat <- matrix(nrow=0, ncol=(ncol(amat)))
    for(i in 1:nrow(amat)) {
        bmat <- rbind(bmat, c(amat[i,1], rollmean(amat[i,], n), amat[i, w]))
    }
    return(bmat)
}

reduce.mat <- function(amat) {
    blocks <- matrix(c(1,3,3,5,6,8,8,10), 4, 2)
    bmat <- matrix(nrow=0, ncol=nrow(blocks))
    for(i in 1:nrow(amat)) {
        x <- amat[i,]
        y <- rep(0,nrow(blocks))
        for(bi in 1:nrow(blocks)) {
            bx <- x[seq(blocks[bi,1], blocks[bi,2])]
            y[bi] <- sum(bx) / length(bx)
        }
        bmat <- rbind(bmat, y)
    }
    return(bmat)
}

read.mat.sf <- function(amin=500, ways.sf=NA) {
    if(is.na(ways.sf)) {
        ways.sf <- read.ways.sf()
    }
    mat.sf <- list2matrix(ways.sf)
    mat.sf <- filter.mat(mat.sf, amin)
    mat.sf <- smooth.mat(mat.sf)
    # mat.sf <- reduce.mat(mat.sf)
    mat.sf <- normalize.mat(mat.sf + 1)
    return(mat.sf)
}

init.centers <- function(n) {
    c1 <- seq(from=0.0, to=1.0, length.out=n)
    c2 <- seq(from=1.0, to=0.0, length.out=n)
    c3 <- 1 - ((seq(1,n) - (1+n)/2)^2)/(n-1)/(n-1)
    return(matrix(c(c1,c2,c3), 3, n))
}

som.sf <- function(mat.sf) {
    library(kohonen)
    fit.som.sf <- som(mat.sf, grid=somgrid(xdim=3,ydim=2), rlen=100, alpha=c(0.05, 0.01), keep.data=T)
    return(fit.som.sf)
}

kmeans.sf <- function(mat.sf, centers=5) {
    # centers <- init.centers(10)
    # centers <- 3
    fit.kmeans.sf <- kmeans(mat.sf, centers=centers, iter.max=10000)
    return(fit.kmeans.sf)
}

amap.km.sf <- function(mat.sf, centers=5) {
    library(amap)
    # method <- 'pearson'
    method <- 'maximum'
    fit.amap.km.sf <- Kmeans(mat.sf, centers=centers, iter.max=10000, method=method)
    return(fit.amap.km.sf)
}

fcm.sf <- function(mat.sf) {
    library(e1071)
    fit.fcm.sf <- cmeans(mat.sf, centers=4, iter.max=1000, verbose=T, dist='euclidean', method='cmeans')
    return(fit.fcm.sf)
}

kkm.sf <- function(mat.sf) {
    library(kernlab)
    fit.kkm.sf <- kkmeans(mat.sf, centers=3, kernel='splinedot')
    return(fit.kkm.sf)
}

kmeans.diff.centers <- function(mat.sf) {
    a <- c()
    for(c in seq(1,16)) {
        fit <- kmeans.sf(mat.sf, centers=c)
        a <- c(a, fit$tot.withinss)
    }
    return(a)
}

plot.clust.som <- function(data, fit) {
    library(cluster)
    clusplot(data, fit$unit.classif, color=T, shade=T, labels=2, lines=0)
}

plot.clust.kmeans <- function(data, fit) {
    library(cluster)
    clusplot(data, fit$cluster, color=T, shade=T, labels=2, lines=0)
}

plot.clust.fcm <- function(data, fit) {
    library(cluster)
    clusplot(data, fit$cluster, color=T, shade=T, labels=2, lines=0)
}

plot.clust.kkm <- function(data, fit) {
    library(cluster)
    clusplot(data, fit$cluster, color=T, shade=T, labels=2, lines=0)
}

plot.clust.amap.km <- function(data, fit) {
    library(cluster)
    clusplot(data, fit$cluster, color=T, shade=T, labels=2, lines=0)
}

plot.sf <- function(data, clust, index, max.num=100) {
    plot(c(0,11), c(0,1), type='n')
    n <- min(max.num, nrow(data))
    for(i in seq(1,n)) {
        if(clust[i] == index) {
            lines(data[i,], type='l', col=i%%200)
        }
    }
}

plot.centers <- function(centers) {
    plot(c(0,11), c(0,1), type='n')
    for(i in seq(1,nrow(centers))) {
        lines(centers[i,], type='l')
    }
}

write.clust <- function(ways.sf, mat.sf.all, centers) {
    source('write_ways.r')
    nc <- nrow(centers)
    nd <- nrow(mat.sf.all)
    clust.sf <- matrix(nrow=nd, ncol=2)
    for(i in seq(1,nd)) {
        if(max(ways.sf[[i]]) < 100) {
            dmin_j <- 0
        }else {
            dmin <- 1/0
            dmin_j <- 0
            for(j in seq(1,nc)) {
                s <- sum((centers[j,] - mat.sf.all[i,])^2)
                if(s < dmin) {
                    dmin_j <- j
                    dmin <- s
                }
            }
        }
        clust.sf[i,1] <- i
        clust.sf[i,2] <- dmin_j        
    }
    colnames(clust.sf) <- c("wid", "clust")
    df <- as.data.frame(clust.sf)
    write.ways(df, "ways_clust")
}

