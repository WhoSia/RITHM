# Independent R-side group-welfare calculation; no inference or packages.
a <- commandArgs(trailingOnly=TRUE)
if(length(a)!=1) stop("Usage: Rscript R/check_study1.R study1.csv")
d <- read.csv(a[1],check.names=FALSE)
stopifnot(all(c("Session","Period","Subject","S","M","LaneS","LaneM","Profit") %in% names(d)))
stopifnot(all(d$S+d$M==18),all(d$LaneS+d$LaneM==1))
earned <- ifelse(d$LaneS==1,40-(12+3*d$S),40-(6+2*d$M))
stopifnot(all(earned==d$Profit))
g <- split(d,paste(d$Session,d$Period,sep=":"))
m <- vapply(g,function(z) {
 stopifnot(nrow(z)==18,length(unique(z$Subject))==18,length(unique(z$S))==1,
           sum(z$LaneS)==z$S[1])
 s <- z$S[1]; w <- -36+66*s-5*s*s
 stopifnot(sum(z$Profit)==w)
 c(s=s,w=w)
},numeric(2))
mu <- mean(m["s",])
variance <- mean((m["s",]-mu)^2)
mw <- mean(m["w",])
at <- -36+66*mu-5*mu*mu
stopifnot(abs((181-at)+5*variance-(181-mw))<1e-8)
cat(sprintf("R_INDEPENDENT_PASS rounds=%d meanW=%.6f meanS=%.6f varS=%.6f\n",
   ncol(m),mw,mu,variance))
