read.ways.sf <- function(hour=NA) {
    source('read_ways.r')

    print(paste('reading ways and attrs with hour = ', hour))
    if(is.na(hour)) {
        df.ways.attrs <- read.ways.attrs(c('id','used_times','used_interval','km','kmh'))
        colname = 'used_interval'
    }
    else {
        df.ways.attrs <- read.ways.attrs.by.hour(hour, c('id','freq','sf','npick','ndrop','km','kmh'))
        colname = 'sf'
    }
    print('generating ways.st')    
    ways.num <- length(df.ways.attrs$id)
    ways.sf <- list(rep(0, ways.num))
    for(i in 1:ways.num) {
        ways.sf[[i]] <- unlist(lapply(strsplit(df.ways.attrs[df.ways.attrs$id == i, colname], ','), as.numeric))
    }

    return(ways.sf)
}

read.ways.attrs.2 <- function(colname) {
    source('read_ways.r')
    ns <- rep(0, 49122)
    for(h in 0:23) {
        df <- read.ways.attrs.by.hour(h, c('id', colname))
        ns <- ns + unlist(df[colname])
    }
    return(ns)
}

read.sum.h <- function(colname) {
    ss <- rep(0,24)
    for(h in 0:23) {
        df <- read.ways.attrs.by.hour(h, c('id', colname))
        ss[h+1] <- sum(df[colname])
    }
    return(ss)
}

plot.sum.h <- function(ss) {
    require(ggplot2)
    df <- data.frame(x=0:23, y=ss)
    p <- ggplot(df, aes(x, y)) + geom_line() 
    p
}

load.var <- function(filename) {
    return(local(get(load(filename))))
}

save.ways.sf.by.hour <- function() {
    for(h in 0:23) {
        ways.sf <- read.ways.sf(h)
        save(ways.sf, file=sprintf("rdata_hour/ways_sf_h%02d.RData", h))
    }
}

read.ways.sf.by.hours <- function(from_h, to_h) {
    ways.sf <- NA
    for(h in from_h:to_h) {
        tmp.sf <- load.var(sprintf("rdata_hour/ways_sf_h%02d.RData", h))
        ways.num <- length(tmp.sf)
        if(is.na(ways.sf)) {
            ways.sf <- tmp.sf
        }else {
            for(i in 1:ways.num) {
                ways.sf[[i]] <- ways.sf[[i]] + tmp.sf[[i]]
            }
        }
    }
    return(ways.sf)
}

save.sf.h <- function() {
    ways.sf.h0811 <- read.ways.sf.by.hours(8, 11)
    save(ways.sf.h0811, file='ways_sf_h0811.RData')
    ways.sf.h1215 <- read.ways.sf.by.hours(12, 15)
    save(ways.sf.h1215, file='ways_sf_h1215.RData')
    ways.sf.h1619 <- read.ways.sf.by.hours(16, 19)
    save(ways.sf.h1619, file='ways_sf_h1619.RData')
    ways.sf.h2023 <- read.ways.sf.by.hours(20, 23)
    save(ways.sf.h2023, file='ways_sf_h2023.RData')
}

load.sf.h <- function() {
    ways.sf.h0811 <<- load.var('ways_sf_h0811.RData')
    ways.sf.h1215 <<- load.var('ways_sf_h1215.RData')
    ways.sf.h1619 <<- load.var('ways_sf_h1619.RData')
    ways.sf.h2023 <<- load.var('ways_sf_h2023.RData')
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
        # bmat[i,] <- amat[i,] / (sum(amat[i,]) + 0.0001)
        # bmat[i,] <- (amat[i,]-amin)/(amax-amin + 1)
        # bmat[i,] <- (amat[i,]-am) / (am+1)
        bmat[i,] <- amat[i,] / (amax + 0.0001)
    }
    return(bmat)
}

wsum.mat <- function(amat) {
    nr <- nrow(amat)
    nc <- ncol(amat)
    bmat <- matrix(nrow=nr, nc=2)
    for(i in 1:nr) {
        s <- 0
        ss <- 0
        for(j in 1:nc) {
            s <- s + amat[i,j]*(j-nc/2)
            ss <- ss + abs(amat[i,j]*(j-nc/2))
        }
        bmat[i,] = c(s,ss)
    }
    return(bmat)
}

# The max element of sf should be bigger than amin
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

read.mat.sf.debug <- function(amin=100, ways.sf=NA) {
    if(is.na(ways.sf[1])) {
        ways.sf <- read.ways.sf()
    }
    mat.sf <- list2matrix(ways.sf)
    mat.sf <- filter.mat(mat.sf, amin)
    mat.sf <- smooth.mat(mat.sf)
    # mat.sf <- reduce.mat(mat.sf)
    mat.sf <- normalize.mat(mat.sf + 1)
    return(mat.sf)
}

read.mat.sf <- function(amin=100, ways.sf=NA, isall=F) {
    if(is.na(ways.sf[1])) {
        ways.sf <- read.ways.sf()
    }
    library(zoo)
    
    amat <- list2matrix(ways.sf)
    w <- ncol(amat)
    
    bmat <- matrix(nrow=0, ncol=ncol(amat))
    for(i in 1:nrow(amat)) {
        amax <- max(amat[i,])
        if(amax > amin) {
            tmp <- c(amat[i,1], rollmean(amat[i,], 3), amat[i, w])
            tmp <- tmp / (max(tmp) + 0.0001)
            bmat <- rbind(bmat, tmp)
        } else if(isall) {
            bmat <- rbind(bmat, rep(-1, 10))
        }
    }
    return(bmat)
}

min.max.loc <- function(amat) {
    bmat <- matrix(nrow=0, ncol=2)
    for(i in 1:nrow(amat)) {
        xs <- amat[i,]
        minloc <- 1
        maxloc <- 1
        amin <- -1
        amax <- -1
        for(j in 1:ncol(amat)) {
            x <- xs[j]
            if(x < amin || amin == -1) {
                amin <- x
                minloc <- j
            }
            if(x > amax || amax == -1) {
                amax <- x
                maxloc <- j
            }
        }
        ys <- array(0,2)
        # minloc <- abs(minloc-5.5)
        ys[1] = minloc
        # maxloc <- abs(maxloc-5.5)
        ys[2] = maxloc
        bmat <- rbind(bmat, ys)
    }
    return(bmat)
}

hist.min.max.loc <- function(amat) {
    require(ggplot2)
    df <- data.frame(minloc=amat[,1], maxloc=amat[,2])
    p <- ggplot(df, aes(minloc, maxloc))
    x <- seq(0.5, 10.5, by=1)
    y <- seq(0.5, 10.5, by=1)
    p <- p + stat_bin2d(drop=F, breaks=list(x=x,y=y))
    # p <- p + scale_fill_gradient(low = "grey", high ="red")
    p
}

hist.wsum <- function(amat) {
    require(ggplot2)
    df <- data.frame(avgloc=amat[,1], avgabs=amat[,2])
    p <- ggplot(df, aes(avgloc, avgabs))
    p <- p + stat_bin2d(drop=F)
    # p <- p + scale_fill_gradient(low = "grey", high ="red")
    p
}

hist.grid.fit <- function(fit.som.sf) {
    require(ggplot2)
    amat <- som.grid.classif(fit.som.sf)
    nx <- fit.som.sf$grid$xdim
    ny <- fit.som.sf$grid$ydim
    hist.grid(amat, nx, ny)
}

hist.grid <- function(amat, nx, ny) {
    require(ggplot2)
    x11()
    df <- data.frame(x=amat[,1], y=amat[,2])
    p <- ggplot(df, aes(x, y))
    x <- seq(0.5, nx+0.5, by=1)
    y <- seq(0.5, ny+0.5, by=1)
    p <- p + stat_bin2d(drop=F, breaks=list(x=x,y=y))
    # p <- p + scale_fill_gradient(low = "grey", high ="red")
    return(p)
}

map.heat <- function(amat) {
    require(ggplot2)
    x11()
    # p <- heatmap(amat)
    data = matrix(0, nrow=nrow(amat)*ncol(amat), 3)
    k = 0
    for(i in 1:nrow(amat)) {
        for(j in 1:ncol(amat)) {
            k = k+1
            data[k,] = c(i,j,amat[i,j])
        }
    }
    df <- data.frame(x=data[,2], y=data[,1], value=data[,3])
    p <- ggplot(df, aes(x, y)) + 
         geom_tile(aes(fill = value), colour = "white") + 
         scale_fill_gradient(low = "grey", high = "red")
    return(p)
}

plot.grid <- function(som.iter.res, all=F, type='l') {
    require(ggplot2)
    x11()
    code <- som.iter.res$code
    pts <- som.iter.res$fit$grid$pts
    nx <- som.iter.res$fit$grid$xdim
    ny <- som.iter.res$fit$grid$ydim
    
    par(mar=c(0.5, 0.5, 0.5, 0.5))
    par(mfrow=c(ny, nx))
    for(i in 1:(nx*ny)) {
        plot(1:ncol(code), code[i,], type=type, lwd=2, bg='red', xlim=c(0,ncol(code)+1), ylim=c(-0.2,1.2), axes=F)
        rect(par("usr")[1],par("usr")[3],par("usr")[2],par("usr")[4],col = "#aaaaaaaa")
        if(all) {
            for(j in 1:length(som.iter.res$codes)) {
                lines(1:ncol(som.iter.res$codes[[j]]), som.iter.res$codes[[j]][i,], type=type, ylim=c(0,1), col='red')
            }
        }
        axis(side=1, seq(0.5, 10.5, 2), labels = F)
        axis(side=2, seq(0.0, 1.0, 0.2), labels = F)
        box()
    }
}

read.clust.catos <- function() {
    source('read_ways.r')
    rs <- read.som.clust()
    catos = rep(0, 100)
    for(r in rs) {
        strs <- strsplit(substr(r, 2, nchar(r)-1),',')[[1]]
        clust <- as.numeric(strs[1])
        cato <- as.numeric(strs[2])
        catos[clust] = cato
    }
    return(catos)
}

plot.grid.ggplot <- function(som.iter.res) {
    require(ggplot2)
    require(grid)

    x11()
    code <- som.iter.res$code
    pts <- som.iter.res$fit$grid$pts
    nx <- som.iter.res$fit$grid$xdim
    ny <- som.iter.res$fit$grid$ydim
    
    catos <- read.clust.catos()

    layout <- matrix(1:100, 10, 10)
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout), just='centre')))

    library(RColorBrewer)
    colors <- brewer.pal(8, 'Pastel2')
    for(i in 1:(nx*ny)) {
        df = data.frame(y=code[i,])
        p <- ggplot(df) + 
             geom_step(aes(x=1:10, y=y), size=0.7) + 
             xlim(0, 11) + 
             ylim(-0.2, 1.2) + 
             theme(plot.margin = unit(rep(0.17, 4), "cm")) + 
             theme(panel.margin = unit(rep(0, 4), "cm")) +
             theme(legend.margin = unit(rep(0, 4), "cm")) +
             theme(panel.background = element_rect(fill=colors[catos[i]])) +  
             theme(axis.ticks=element_blank()) + 
             theme(axis.text=element_blank()) +
             theme(axis.title=element_blank()) +
             theme(axis.line=element_blank()) + 
             theme(axis.ticks.length=unit(0, "mm")) +
             theme(axis.ticks.margin=unit(0, "mm")) +
             labs(x=NULL, y=NULL)
        matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
        print(p, vp = viewport(layout.pos.row = matchidx$col, layout.pos.col = matchidx$row))
    }
}

cato.legend <- function() {
    library(reshape2) # for melt
    library(RColorBrewer)
    colors <- brewer.pal(8, 'Pastel2')
    print(colors)
    mx <- matrix(0, 8, 3)
    k <- 1
    for(i in 1:4) {
        for(j in 1:2) {
            mx[k,] <- c(i,j,k)
            k <- k+1
        }
    }
    df <- data.frame(mx)
    p1 <- ggplot(df, aes(x=X1, y=X2, fill=factor(X3))) + geom_tile() + 
          scale_fill_manual(values=colors, guide = guide_legend(title="Category: ", tile.vjust = -5, 
                                                                keywidth = 1, keyheight = 1, 
                                                                label.position='top', label.hjust = 0.5, label.vjust=2)) + 
          theme(legend.position="bottom") + 
          theme(legend.text=element_text(family='sans', face='bold')) 
    return(p1)
}

print.som.cat <- function() {
    source('read_ways.r')
    rs <- read.som.clust()
    for(r in rs) {
        strs <- strsplit(substr(r, 2, nchar(r)-1),',')[[1]]
        clust <- as.numeric(strs[1])
        cato <- as.numeric(strs[2])
        cat(sprintf("%2d", cato))
        if(clust %% 10 == 0) {
            cat("\n")
        }
    }
    flush.console()
}

plot.grid.fit <- function(fit, mat.sf, all=F, type='l') {
    require(ggplot2)
    x11()
    code <- fit$code
    pts <- fit$grid$pts
    nx <- fit$grid$xdim
    ny <- fit$grid$ydim
    classif <- fit$unit.classif

    par(mar=c(1, 1, 1, 1))
    par(mfrow=c(ny, nx))
    for(i in 1:(nx*ny)) {
        plot(1:ncol(code), code[i,], type=type, ylim=c(0,1), axes=F)
        if(all) {
            for(j in 1:length(classif)) {
                if(classif[j] == i) {
                    lines(1:10, mat.sf[j,], type=type, ylim=c(0,1))
            
                }
            }
        } 
    }
}

u.mat.som <- function(code, nx, ny) {
    bmat <- matrix(0, nrow=ny, ncol=nx)
    ng <- matrix(c(0,1,0,-1,1,0,-1,0), 4, 2, byrow=T)
    # ng <- matrix(c(0,1,0,-1,1,0,-1,0,1,1,1,-1,-1,1,-1,-1), 8, 2, byrow=T)

    for(i in 1:ny) {
        for(j in 1:nx) {
            s = 0
            sk = 0
            for(k in 1:nrow(ng)) {
                ii = i + ng[k,1]
                jj = j + ng[k,2]
                if(ii >= 1 && ii <= ny && jj >= 1 && jj <= nx) {
                    s = s + sqrt(sum((code[(ii-1)*ny+jj,] - code[(i-1)*ny+j]) ^ 2))
                    sk = sk + 1
                }
            }
            bmat[i,j] <- s/sk
        }
    }
    return(bmat)
}

plot.grid.som <- function(fit.som.sf) {
    x11()
    plot(fit.som.sf, type='codes', codeRendering='lines')
}

read.mat.sf.loc <- function(amin=100, ways.sf=NA) {
    if(is.na(ways.sf)) {
        ways.sf <- read.ways.sf()
    }
    mat.sf <- list2matrix(ways.sf)
    mat.sf <- filter.mat(mat.sf, amin)
    mat.sf <- min.max.loc(mat.sf)
    return(mat.sf)
}

init.centers <- function(n) {
    c1 <- seq(from=0.0, to=1.0, length.out=n)
    c2 <- seq(from=1.0, to=0.0, length.out=n)
    c3 <- 1 - ((seq(1,n) - (1+n)/2)^2)/(n-1)/(n-1)
    return(matrix(c(c1,c2,c3), 3, n))
}

som.sf <- function(mat.sf, rlen=100, xdim=3, ydim=2) {
    library(kohonen)
    fit.som.sf <- som(mat.sf, 
                      grid=somgrid(xdim=xdim,ydim=ydim), 
                      rlen=rlen, 
                      # radius=c(10,1),
                      alpha=c(0.1, 0.01), 
                      n.hood='circular', keep.data=T)
    return(fit.som.sf)
}

som.sf.iter <- function(mat.sf, rtime=5,  rlen=100, xdim=3, ydim=2) {
    grid <- matrix(0, nrow=0,ncol=2)
    heat <- matrix(0, nrow=ydim, ncol=xdim)
    code <- matrix(0, nrow=xdim*ydim, ncol=ncol(mat.sf))
    codes <- list()
    i = 0
    while(i<rtime) {
        fit <- som.sf(mat.sf, rlen, xdim, ydim)
        fit <- rotate.grid(fit)
        if(which.max(fit$codes[1,]) >= 9 && 
           which.max(fit$codes[xdim,]) <= 2 && 
           any(which.max(fit$codes[xdim*(ydim-1)+1,]) == 4:7) &&
           any(which.max(fit$codes[xdim*ydim,]) == 4:7)) 
        {
            tmpgrid <- som.grid.classif(fit)
            # grid <- rbind(grid, tmpgrid)
            for(j in 1:nrow(tmpgrid)) {
                heat[tmpgrid[j,2], tmpgrid[j,1]] = heat[tmpgrid[j,2], tmpgrid[j,1]] + 1
            }
            code <- code + fit$codes
            codes[[i+1]] <- fit$codes
            pts <- fit$grid$pts
            i = i+1
            print(sprintf('iter:%d',i))
        } else {
            print(sprintf('N, %d, %d, %d, %d', 
                  which.max(fit$codes[1,]),
                  which.max(fit$codes[xdim,]),
                  which.max(fit$codes[xdim*(ydim-1)+1,]),
                  which.max(fit$codes[xdim*ydim,])))
        }
    }
    res = list(
               grid=grid,
               heat=heat, 
               code=code/rtime, 
               codes = codes,
               fit=fit)
    return(res)
}

rotate.grid <- function(fit) {
    rotate <- function(x) apply(x, 1, rev)

    nx <- fit$grid$xdim
    ny <- fit$grid$ydim
    m <- matrix(1:(nx*ny), ny, nx, byrow=T)
    i = 0
    while(which.max(fit$codes[m[1,1],]) < 9 && i<4) {
        m <- rotate(m)
        i = i+1
    }
    if(i == 4) {
        return(fit)
    }
    if(which.max(fit$codes[m[ny,1],]) <= 2) {
        m <- t(m)
    }
    pts <- fit$grid$pts
    code <- matrix(0, nx*ny, ncol(fit$codes))
    classif <- rep(0, length(fit$unit.classif))
    for(i in 1:(nx*ny)) {
        ii = m[pts[i,2],pts[i,1]]
        code[i,] <- fit$codes[ii,]
    }
    nn <- length(classif)
    for(i in 1:nn) {
        ii = m[pts[fit$unit.classif[i],2],pts[fit$unit.classif[i],1]]
        classif[i] <- fit$unit.classif[ii]
    }
    fit$codes <- code
    fit$unit.classif <- classif
    return(fit) 
}

kmeans.sf <- function(mat.sf, centers=5) {
    # centers <- init.centers(10)
    # centers <- 3
    fit.kmeans.sf <- kmeans(mat.sf, centers=centers, iter.max=10000)
    return(fit.kmeans.sf)
}

kmeans.tot.withinss <- function(mat.sf, centers=1:10) {
    ss <- rep(0, length(centers))
    i = 0
    for(c in centers) {
        fit <- kmeans.sf(mat.sf, c)
        i = i+1
        ss[i] <- fit$tot.withinss
    }
    x11()
    plot(1:i, ss)
}

kcents.dist <- function(x, centers) {
    nx <- nrow(x)
    nc <- nrow(centers)
    z <- matrix(0, nx, ncol = nc)
    for(i in 1:nx) {
        for(j in 1:nc) {
            z[i, j] <- euclid.dist(x[i,], centers[j,])
        }
    }
    return(z)
}

euclid.dist <- function(a, b) {
    return(sqrt(sum((a-b)**2)))
}

kcents.sf <- function(mat.sf, centers=5) {
    library(flexclust)
    fit.kcents.sf <- kcca(mat.sf, k=centers, family=kccaFamily(dist=kcents.dist, cent=centMean), save.data=F)
    return(fit.kcents.sf)
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
    fit.fcm.sf <- cmeans(mat.sf, centers=5, iter.max=1000, verbose=T, dist='euclidean', method='cmeans')
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

som.grid.classif <- function(fit) {
    classif <- fit$unit.classif
    nr <- length(classif)
    pts <- fit$grid$pts
    bmat <- matrix(nrow=nr, ncol=2)
            
    for(i in 1:nr) {
        bmat[i,] = pts[classif[i],]
    }
    return(bmat)
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
    x11()
    plot(c(0,11), c(0,1), type='n')
    n <- min(max.num, nrow(data))
    for(i in seq(1,n)) {
        if(clust[i] == index) {
            lines(data[i,], type='l', col=i%%200)
        }
    }
}

# for som, arg 'center' should be fit.som.sf$codes, 
# for som iter, arg 'center' should be fit.som.sf$code, 
# otherwise, fit.method.sf$centers
plot.centers <- function(centers) {
    x11()
    plot(c(0,11), c(0,1), type='n')
    for(i in seq(1,nrow(centers))) {
        lines(centers[i,], type='l')
    }
}

all.ways.clust <- function(ways.sf, mat.sf.all, minsf, centers) {
    nc <- nrow(centers)
    nd <- nrow(mat.sf.all)
    clust.sf <- matrix(nrow=nd, ncol=2)
    for(i in seq(1,nd)) {
        if(max(ways.sf[[i]]) < minsf) {
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
    return(clust.sf)
}

cato.by.hours <- function(from_h, to_h) {
    ways.sf <- read.ways.sf.by.hours(from_h, to_h)
    mat.sf <- read.mat.sf(amin=100, ways.sf, isall=F)
    mat.sf.all <- read.mat.sf(amin=100, ways.sf, isall=T)
    
    fit.som.sf <- som.sf.iter(mat.sf, rtime=50,  rlen=100, xdim=10, ydim=10)
    ways.clust <- all.ways.clust(ways.sf, mat.sf.all, 100, fit.som.sf$code)
    
    catos <- read.clust.catos()
    ways.catos <- apply(ways.clust, 1, function(x) if(x[2] == 0){0} else{catos[x[2]]})
    return(as.numeric(ways.catos))
}

hist.catos <- function(catos=NA) {
    x11()
    source('read_ways.r')
    if(is.na(catos)) {
        catos <- read.ways.cato()
    }
    catos <- data.frame(catos)
    names(catos) <- c('X')
    catos <- catos[catos$X > 0,]
    catos <- data.frame(catos)
    names(catos) <- c('X')
    library(RColorBrewer)
    colors <- brewer.pal(8, 'Pastel2')
    colors <- c("#24B373", "#E6782E","#1761E9","#DA2C97","#96CD29","#DAB916","#F3C992","#C0C0C0")
    print(colors)
    p <- ggplot(catos, aes(factor(X), fill=factor(X))) + geom_bar() + 
         scale_fill_manual(values=colors)
    p
}

hist.catos.freq <- function() {
    x11()
    source('read_ways.r')
    df <- read.ways.attrs(c('used_times'))
    df$cato <- read.ways.cato()
    only <- c(1,2,8)
    df <- df[df$cato %in% only, ]
    library(RColorBrewer)
    colors <- c("#24B373", "#E6782E","#1761E9","#DA2C97","#96CD29","#DAB916","#F3C992","#808080")
    colors <- colors[only]
    p <- ggplot(df, aes(used_times, colour=factor(cato))) + geom_density() + 
         scale_color_manual(values=colors)
    p
}

hist.catos.kmh <- function() {
    x11()
    source('read_ways.r')
    df <- read.ways.attrs(c('kmh'))
    df$cato <- read.ways.cato()
    only <- c(1,2,8)
    df <- df[df$cato %in% only, ]
    library(RColorBrewer)
    colors <- c("#24B373", "#E6782E","#1761E9","#DA2C97","#96CD29","#DAB916","#F3C992","#808080")
    colors <- colors[only]
    p <- ggplot(df, aes(kmh, colour=factor(cato))) + geom_density() + 
         scale_color_manual(values=colors)
    p
}

hist.catos.km <- function() {
    x11()
    source('read_ways.r')
    df <- read.ways.attrs(c('km'))
    df$cato <- read.ways.cato()
    only <- c(1,2,8)
    df <- df[df$cato %in% only, ]
    library(RColorBrewer)
    colors <- c("#24B373", "#E6782E","#1761E9","#DA2C97","#96CD29","#DAB916","#F3C992","#808080")
    colors <- colors[only]
    p <- ggplot(df, aes(km, colour=factor(cato))) + geom_density() + 
         scale_color_manual(values=colors)
    p
}

hist.catos.npd <- function() {
    x11()
    source('read_ways.r')
    df <- read.ways.attrs(c('heat'))
    df$cato <- read.ways.cato()
    only <- c(1,2,8)
    df <- df[df$cato %in% only, ]
    df <- df[df$heat < 200, ]
    library(RColorBrewer)
    colors <- c("#24B373", "#E6782E","#1761E9","#DA2C97","#96CD29","#DAB916","#F3C992","#808080")
    colors <- colors[only]
    p <- ggplot(df, aes(heat, colour=factor(cato))) + geom_density() + 
         scale_color_manual(values=colors) + 
         scale_y_continuous(limits = c(0, 0.05))
    p
}

diff.cato.by.hours <- function() {
    catos.h0811 <<- cato.by.hours(8,  11)
    catos.h1215 <<- cato.by.hours(12, 15)
    catos.h1619 <<- cato.by.hours(16, 19)
    catos.h2023 <<- cato.by.hours(20, 23)
}

load.catos <- function() {
    catos.h0811 <<- load.var('catos_h0811.RData')
    catos.h1215 <<- load.var('catos_h1215.RData')
    catos.h1619 <<- load.var('catos_h1619.RData')
    catos.h2023 <<- load.var('catos_h2023.RData')
    catos.h <<- cbind(catos.h0811, catos.h1215, catos.h1619, catos.h2023)
}

find.any.diff.cato <- function(catos.h) {
    nc = ncol(catos.h)
    which(apply(catos.h, 1, function(x) {
        for(i in 1:(nc-1)){
            if(x[i] == 0) {
                return(F)
            }
            for(j in (i+1):nc){
                if(x[i] != x[j]) {
                    return(T)
                }
            }
        }
        return(F)
    }))
}

find.all.diff.cato <- function(catos.h) {
    nc = ncol(catos.h)
    which(apply(catos.h, 1, function(x) {
        for(i in 1:(nc-1)){
            if(x[i] == 0) {
                return(F)
            }
            for(j in (i+1):nc){
                if(x[i] == x[j]) {
                    return(F)
                }
            }
        }
        return(T)
    }))
}

find.opp.diff.cato <- function(catos.h) {
    nc = ncol(catos.h)
    which(apply(catos.h, 1, function(x) {
        if(1 %in% x && 8 %in% x) { 
            return(T)
        }
        return(F)
    }))
}

count.catos <- function(catos) {
    sapply(0:8, function(x) sum(catos == x))
}

write.clust <- function(ways.sf, mat.sf.all, minsf, centers, tbname) {
    source('write_ways.r')
    clust.sf <- all.ways.clust(ways.sf, mat.sf.all, minsf, centers)
    df <- as.data.frame(clust.sf)
    write.ways(df, tbname)
}

heat.map <- function() {
    library(ggmap) 
    myUni=mydata[!duplicated(mydata$ClientID),] # produce dataframe with unique individuals
    mywhere=merge(myUni, mycodes, by.x="ClientHomePostcode",
                            by.y="Postcode", all=FALSE) # merge with postcode data
 
    ### Plot!
 
    # map.center = geocode(&quot;Nottingham, UK&quot;) # Centre map on Nottingham
    map.center = geocode("Tsinghua University of China")
    myMap = qmap(c(lon=map.center$lon, lat=map.center$lat),
                           source="google", zoom=10) # download map from Google
    map <- qmap(location = 'Beijing', zoom = 10, maptype = 'roadmap')

    myMap + stat_bin2d(bins=80, aes(x=Long, y=Lat), alpha=.6, data=mywhere) + 
    scale_fill_gradient(low = "blue", high ="red")
    # plot with a bit of transparency
    myMap
}


compute.save.all <- function() {
    save.ways.sf.by.hour()
    # mat.sf <- read.mat.sf()
    # som.iter.res <- som.sf.iter(mat.sf)
    # save(som.iter.res, file="res10.RData")
}

if(F) {
    setEPS()
    
    postscript("../../../paper/way1.eps")
    dev.off()
}
