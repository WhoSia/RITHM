# RITHM-2.10 P3-R27-R3 — Switching Friction, Private–Social Adjustment Wedges & Exact Dynamic Welfare

**2026-11-10 — synthetic mathematical study and Research OS source intake. No new human-source model fitting in this unit.**

## Return to founding question

The original explanatory target is **private behavioral friction → repeated route adjustment → collective congestion/stability → total economic welfare**, not another endless latent-identification microbranch. R27-R2 studied logit reaction to past occupancy/inertia; R27-R3 makes a switching resource cost explicit and separates *actual resource switching costs* from *unobserved psychological status quo bias*. Parameter `s` in this study is a real cost paid upon individual route change, counted in the social objective; it is **not** measured laziness or inferred from the same R23 inertia coefficient.

## Micro-to-macro exact incentive wedge

Six drivers choose A/B. Per-user congestion costs: `c_A(n)=n`, `c_B(n)=2(6-n)`, `C(n)=24+3(n−4)^2`. On a **single unilateral B→A switch** from count n to n+1, the individual *gross* congestion improvement is `g_i=11−3n`, while the societal gross congestion improvement is `g_S=C(n)−C(n+1)=21−6n`. For an **A→B switch**, `g_i=3n−14`, `g_S=6n−27`. The exact externality wedge is `g_S−g_i` and the net gains are `g_i−s`, `g_S−s` when s is an actual resource cost.

Thus at n=3 and B→A: individual gain=2, social gain=3, so **2<s<3** generates locally privately rational refusal despite positive social net return. At n=5 and A→B: private=1 and social=3, so **1<s<3** is a second mismatch. These are single-switch *local counterfactuals*; they are not Nash equilibrium existence claims or exact full-process welfare causal estimates.

## A stochastic 448-state dynamic implementation

Markov state `X_t=(Y_(t-1),N_(t-2))`, 6 labelled binary decisions + one older count. Signal `n_est=(1−w)N_(t−1)+w N_(t−2)`. Personal logit choice probability is constructed by comparing **predicted unilateral cost of remaining versus switching if other actors held their previous routes**, with switching cost s and beta sensitivity. For previous B, `logit(p_A)=beta*(11−3*n_est−s)`; for previous A, `logit(p_A)=beta*(14−3*n_est+s)`. The specific self-impact correction and complete-information count estimate are modeling assumptions; they do not establish individual belief formation. Choices are simultaneous and actual current congestion depends on all choices, so the unilateral forecast need not be correct.

Conditional independence when `tau=0`; when `tau>0`, a symmetric fair binary group shock shifts each individual's probability by `± tau*(2Y_prev−1)*min(p,1−p)`, retaining *every* history-conditional marginal. Exactly propagate 448-state distributions for H=40 (no Monte Carlo noise). The social cost per period is `C(N_t)+s * number_of_personal_route_switches_t`. Distinguish congestion component, switching resource component, group count turnover, and individual switching rate.

### Selected nonfitted exact 40-period results (beta=.6, w=0, tau=0)

| Switching cost s | Expected mean congestion | Mean individual switches per group | Mean total resource social cost |
|---:|---:|---:|---:|
| 0 | 47.559294 | 5.234775 | **47.559294** |
| 2 | 31.649639 | 2.373012 | **36.395663** |
| 4 | 25.174606 | 0.438773 | **26.929698** |
| 6 | 24.823154 | 0.135951 | **25.638862** |
| 7.25 | 24.915624 | 0.074819 | **25.458065** |
| 8 | 25.075545 | 0.054994 | **25.515500** |
| 10 | 25.945932 | 0.028167 | **26.227599** |

**Decision:** In this parametric synthetic family, s>0 can lower expected *total* social resource cost relative to s=0 because it suppresses excessive synchronous responses. Excessive s then raises total cost through prolonged persistence. The smallest in this selected grid is at s=7.25; **there is no global optimum proof, no estimated real-world welfare benefit, no claim that administrative costs ought to be added**. The apparent optimal positive resource friction is model- and information-dependent, and an actual *policy* that imposes friction should be compared against less costly coordination mechanisms.

Additional controlled contrasts: beta=.6,w=.5,tau=0 has mean total cost 34.525520 at s=0, 25.498807 at s=7.25, 26.195015 at s=10; beta=.6,w=0,tau=.6 gives 47.476583 at s=0, 25.525416 at s=7.25, 26.239059 at s=10. Higher-level concerns include non-causal model comparisons, social planner alternative information design and optimal subsidies/tolls, sunk costs versus actual resource cost, and finite Markov chain vs deterministic local instability.

## Source reading and canonical file moves

On 2026-11-10 the user-supplied common 00_INTAKE was audited and eight bibliographically identified PDFs moved **without changing Drive IDs**: Horowitz (1984), Caballero & Engel (1993), Samuelson & Zeckhauser (1988), Klemperer (1987), Rosenthal (1973), and Soucha & Bogdanov (2020) to shared `10_PAPERS`; image-only Smith (1984) and O'Donoghue & Rabin (1999) to `12_IMAGE_SCANS` pending reliable full-text extraction. All eight renamed to the CURRENT `Author(s) (YEAR) — Full Published Title.pdf` grammar, stripped mutable flags/DOI/venue from filename, source metadata retained here; readback verified new parents. No unrelated intake or HOLD objects were disturbed.

### Actual content notes from identified primary source

1. **Horowitz (1984)**, [Drive](https://drive.google.com/file/d/16HGHq4Vv8xSPMQmv1YHmqIsx6taCer8q/view): establishes that unique stochastic two-link equilibrium does not ensure day-to-day convergence. Three distinct information-acquisition/update assumptions: past weighted observed route costs; perceptions fed by own experience and external sources; **own travel experience only**. Depending on updates, link volumes may oscillate, converge very slowly or approach non-equilibrium histories. Direct and serious prior-art limit on claiming feedback instability novel.
2. **Caballero & Engel (1993)**, [Drive](https://drive.google.com/file/d/18SaVLo-ZIewWUrPOA0Ul4EeHbTkOwNXN/view): state-dependent adjustment hazard governs probability of lumpy micro adjustment as gap to moving target grows; aggregate dynamics depend on cross-sectional distribution, including high moments. Important donor for next `hazard(gap)` update instead of treating friction as linear logit intercept.
3. **Samuelson & Zeckhauser (1988)**, [Drive](https://drive.google.com/file/d/14yL8dMpVKaIGZYFXIOMD9g4cPDsKlyc2/view): empirical experimental and retirement/health-plan status quo bias; distinguish rational transition cost, loss aversion/reference-point asymmetry, past-investment/sunk-cost psychological commitments. Mere choice persistence does not identify effort or resource cost.
4. **Klemperer (1987)**, [Drive](https://drive.google.com/file/d/1olKjQAlXObCgxna5mI-HWksGpuIHwFLa/view): switching costs include transaction, learning, artificial contractual costs; alter firms' ex-ante and ex-post competition in opposite directions. Congestion fixed-cost interpretation and oligopoly strategic prices are different environments; do not import the market welfare sign mechanically.
5. **Rosenthal (1973)**, [Drive](https://drive.google.com/file/d/1nn02IV_5_Fd_9HnV-VUogP8-ojNa2xa1/view): pure-strategy equilibrium existence for the described congestion class via cumulative-resource-cost potential construction. Potential minimization **is not** equivalent to social congestion cost minimization: avoid conflating route choice Nash dynamics and n=4 planner optimum.
6. **Smith (1984)** and **O'Donoghue & Rabin (1999)**: actual PDF page images visually inspected and identities established; scans preserved in `12_IMAGE_SCANS`; full symbol-level visual reading / OCR has NOT been claimed. Smith Lyapunov traffic adjustment; O'Donoghue–Rabin present bias/procrastination and sophisticated-versus-naive control.
7. **Soucha & Bogdanov (2020)**: unrelated to traffic but belongs in global shared paper store, with adaptive distinguishing sequences for finite state machines. Abstract/method-level triage; cross-lab transfer cannot be asserted without separate study.

### Updated missing-source priorities (canonical Drive title/author search, not byte-level global exhaustive)

- **Marden & Shamma (2012)**, *Revisiting Log-Linear Learning - Asynchrony, Completeness and Payoff-Based Implementation* (Games and Economic Behavior 75(2), 788-808; DOI 10.1016/j.geb.2012.03.006): asynchronous vs simultaneous update; payoffs and stochastic stability. DOI [source](https://doi.org/10.1016/j.geb.2012.03.006). Search-based absent.
- **Caplin & Spulber (1987)**, *Menu Costs and the Neutrality of Money* (QJE 102(4)): asynchronous lumpy adjustment aggregation; [NBER legal version](https://www.nber.org/papers/w2311). Search-based absent. Note production/prices not transport; method transfer must be explicit.
- **Sandholm (2010)**, *Population Games and Evolutionary Dynamics* (MIT Press): population revision protocols and stochastic stability; monograph full bytes absent on title search, publisher preview is not full book.
- **Dixit & Pindyck (1994)**, *Investment under Uncertainty* (Princeton): irreversible choices and real option value of not adjusting; monograph full bytes absent on title search.
- **Brock & Durlauf (2001)**, *Discrete Choice with Social Interactions*: already possessed, not missing; **Young (1993)**, *The Evolution of Conventions*, and **Kandori, Mailath & Rob (1993)** already possessed. Do not list them as missing.

## Testing, authority and next work

Source-free local implementation of same equations: **9 tests PASS** including 448 conditional probability kernels, all individual-marginal invariances, exact single-move wedges and cost-accounting. GitHub has the published source and its own 8-test synthetic regression plus CI registration; exact default-branch checkout test and remote Actions PASS remain HOLD. Historical original 24-session participants were **not** used to fit s or beta in this R27-R3 study.

**RAVEL RETURN:** Need separate genuine micro-experience/update hazard and nonresource psychological bias in `K_theta`; compare (i) freely adapting users (ii) exogenously costly adjustment (iii) asynchronous switching (iv) informative smoothing / planner coordination. Dynamic objective must include actual resource costs, avoid welfare arbitrage through added real friction; choose interventions that reproduce coordination benefits without resource waste. Strongest scientific question is when **private adjustment inertia stabilizes system without sacrificing individual/societal incentives**, not generic ‘laziness causes inefficiency’.
