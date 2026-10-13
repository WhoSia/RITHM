# R statistical and source-descriptive audit (requires R; no external packages).
# This script MUST NOT infer receipt/attention/policy treatment causality.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop('usage: Rscript validate_group_welfare.R states.csv cpp.csv')
d <- read.csv(args[[1]], stringsAsFactors=FALSE)
x <- read.csv(args[[2]], stringsAsFactors=FALSE)
stopifnot(nrow(d)==480L, length(unique(d$session))==6L,
  all(d$n1+d$n2+d$n3==12L),
  all(d$theoretical_group_cost==264-24*d$n1-9*d$n2+2*d$n1^2+2*d$n1*d$n2+d$n2^2+19*d$incident*d$n2))
stopifnot(nrow(x)==9L, all(x$N==480L))
lookup <- x[x$scheme=='unrestricted' & x$k==1,]
stopifnot(lookup$both==369L,lookup$benefit==376L,lookup$harm==472L)
incident <- x[x$scheme=='incident_avoid' & x$k==1,]
stopifnot(incident$harm==0L,incident$benefit==46L,incident$mean_lower==0)
by_sess <- aggregate(theoretical_group_cost ~ session + info, data=d, FUN=mean)
a <- subset(by_sess,info==0)[order(subset(by_sess,info==0)$session), ]
b <- subset(by_sess,info==1)[order(subset(by_sess,info==1)$session), ]
stopifnot(identical(a$session,b$session))
paired <- b$theoretical_group_cost - a$theoretical_group_cost
cat(sprintf('R_AUDIT_PASS six_sessions=%d group_rounds=%d\n', length(paired),nrow(d)))
cat('Original six-session descriptive info-minus-blind means (NOT causal mediation):\n')
print(data.frame(session=a$session,info_minus_blind_cost=round(paired,4)))
cat(sprintf('mean information-minus-blind TSTC = %.6f\n',mean(paired)))
cat('WARNING: Historical humans, treatment order/carryover and source cost discrepancies; no independent external replication.\n')
