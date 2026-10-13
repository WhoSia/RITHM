# RITHM-2.7 P28 session-aware descriptive audit; not executed in this container.
# Usage: Rscript R/session_audit.R results/p28_panel_bounds.csv
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=1) stop('Pass de-identified 432-row panel bounds CSV')
x <- read.csv(args[1], stringsAsFactors=FALSE)
stopifnot(nrow(x)==432, length(unique(x$session))==6L,
          length(unique(x$policy))==3L, all(x$lower_total <= 0),
          all(x$upper_total >= 0))
stopifnot(all(x$lifetime_budget_B %in% c(0,1,2,4,8,12)))
# Six sessions, NOT 480 independent randomization units. Both treatment arms
# share sessions and participants, so aggregate margins are descriptive only.
for (policy in unique(x$policy)) {
  y <- x[x$policy==policy,]
  for (b in sort(unique(y$lifetime_budget_B))) {
    t <- y[y$lifetime_budget_B==b,]
    by_session <- aggregate(cbind(lower_total,upper_total)~session, t, sum)
    cat(sprintf('%s B=%d: per-480-round range [%.6f, %.6f] source units; session-upper min-max [%.1f, %.1f]\n',
       policy, b,sum(by_session$lower_total)/480,sum(by_session$upper_total)/480,
       min(by_session$upper_total),max(by_session$upper_total)))
  }
}
cat('Audit does NOT establish actual information reading, randomized policy effect, or dynamic traffic feedback.\n')
