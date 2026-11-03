# RITHM-2.10 — Mechanism Identifiability in Repeated Resource Choice

Status: OPEN exploratory research generation, 2026-11-03. RITHM-2.9 closes as an organizing generation; unfinished empirical and CI claims remain inherited HOLD. The historic Lab name and repository slug remain unchanged.

## Central question
What can repeated individual route choices and group turnover reveal about inertia, shared latent environments, information restrictions, strategic coordination and paid deliberation? Where do distinct mechanisms have exactly the same observed distribution?

## Evidence inherited, not automatically promoted
Original author-approved Noussair–Qiao [Drive ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view): 24 sessions, 34,560 choices, 5,616 group transitions. Previous results and limitations in [2.9 Notion](https://app.notion.com/p/3feef561cf9281bcbd77eeb6c983557e). Exploration found residual cross-moment +0.0512449 (session-bootstrap 95% [+0.0335472,+0.0704264]); this is not evidence of causal strategic coordination.

Past 2.9 published Ruby had missing inter-module APIs; the actor-Markov methods and per-session evaluation API were repaired in GitHub commits b717c893 and 31ceab9c. The exact repository SHA has not yet been re-executed against source data with an independently confirmed GitHub Actions run and job log. EWA/EWA+inertia six-fold comparator remains unmatched.

## P0 exact falsifier
Fix a actors previously on route A and (6-a) actors previously on B. Let hidden, fair, shared group-period state Z be +/-1. Conditional on Z, all actors change routes independently, each with probability p + delta*Z. Let U be B-to-A switch count and D be A-to-B. Assuming 0<=p-delta<=p+delta<=1:

E[U]=(6-a)p; E[D]=ap.
E[(U-E[U])*(D-E[D])] = a(6-a)*delta^2.

Thus strictly positive joint turnover residuals can arise without any strategic coordination. For a=3, p=1/2, delta=3/40, exact rational value is 81/1600=0.050625. The numerical closeness to the prior observed 0.05124 is illustrative, NOT an estimated fit to actual data.

## Research tracks
P0: prove exact finite counterexamples and characterize observational equivalence.
P1: calibrate actor switch probabilities by treatment/route/cost/period, then test conditional residuals.
P2: compare latent group shocks, correlated unobserved heterogeneity and strategic interaction on identical legal information/folds.
P3: find existing source variation or independent measurements sufficient to discriminate mechanisms, without recruiting human subjects.
P4: reconnect bounded cognition, friction and downstream collective welfare; specify resource prices and legal clocks.
P5: original-source R and Ruby cross-replay and matched EWA/Markov/oracle comparison before manuscript promotion.

## Operational doctrine
Ruby mainline and Minitest. GitHub Actions may run read-only tests but MUST NOT author commits as github-actions[bot]. Drive holds raw-byte originals; GitHub holds executable and verifiers; Notion logs scientific choices after each substantive unit. Distinguish local unit test, published commit, CI run verified by logs, real-data verification and causal inference. No public re-upload of original human data by default.

## Ruby source
[P0 exact counterexample](p0/latent_common_shock.rb), [Minitest](p0/test_latent_common_shock.rb). Local 3.3.8 test: 4 runs, 6 assertions, 0 failures. Remote CI not yet independently confirmed.
