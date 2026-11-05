# RITHM-2.10 P3-R16A — 00 Intake, Canonical Prior Art and Exact Finite-Welfare Negative Control

Date: 2026-11-05. Status: **literature and synthetic mathematics verified; original-human-data/full empirical R16 and causal novelty HOLD**.

## I. Provenance and correction of the earlier missing-paper list

Two earlier "possibly missing" rival studies already existed in the canonical **10_PAPERS — Canonical Literature Commons** folder (Drive parent ID `1D2M4LHcejREhlyp6vTd71xxLLx-6ldUP`). This is a search-recall failure, not an absence or new acquisition.

1. **Qi, Jia, Qu & He (2024)**, *Investigating Day-to-Day Route Choices Based on Multi-Scenario Laboratory Experiments, Part II: Route-Dependent Attraction-Based Stochastic Process Model*, Communications in Transportation Research **4**, 100123, DOI `10.1016/j.commtr.2024.100123`. Canonical [Drive PDF](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view), 16 pages, source raw SHA256 `36f20f6884a2d1b680c0ee78f6921d530e176feb54c29c3874b9af469fd45ef6`. Source sections 2–6: route-dependent attraction, inertia/preferences, independent binomial individual switch counts and Poisson-binomial route flows, finite-state irreducible/aperiodic Markov process, empirical switching/flow-distribution tests, approximate equilibrium distribution and short/long-run policy implications; experimental samples span 312 subjects across eight scenarios. **We cannot claim these are novel RITHM ideas.** Their Markov model deliberately uses less historical information than some RL learners; any comparison should respect that distinction.
2. **Cantarella & Watling (2016)**, *A General Stochastic Process for Day-to-Day Dynamic Traffic Assignment: Formulation, Asymptotic Behaviour, and Stability Analysis*, Transportation Research Part B, DOI `10.1016/j.trb.2016.05.005`. Canonical [Drive author PDF](https://drive.google.com/file/d/1oFYvFMXekKqDcdgu6Om8vNEz1zfcaLBx/view), 19 pages, source SHA256 `bef05af5a00e682430dd009c3839289d8529c1672773c26926e1c4e7903461c6`. Sections 3–5: habit via persistence, learning via memory/smoothing, conditional independent route choices, mean process and its asymptotic stability relative to SUE, distinction between mean and variance. Their Results 1–4 already separate mean trajectories, equilibrium invariance, parameter-dependent stability and variance dependence beyond means. **Mean-vs-variance mismatch is prior art.**

Inspected the dedicated [00_INTAKE — Literature Radar](https://drive.google.com/drive/folders/1MLtYh0pv8QUZDReYzRqjDrOjRkSJAD16): two ambiguous file names contain relevant prior art:
3. `smith2013.pdf` is the publisher PDF of Smith, Hazelton, Lo, Cantarella & Watling, *The Long Term Behaviour of Day-to-Day Traffic Assignment Models*, Transportmetrica A **10** (2014), 647–660, DOI `10.1080/18128602.2012.751683` (published online 30 Jan 2013), [00 original](https://drive.google.com/file/d/11o1ZPHaCSA2GY9ZDnOU_JgizfI1DKQcA/view), local SHA `2afa8308c1fb09d87edf912c0751c92a3bc55576ef2e4150b7a3624fb0376407`. The canon already contains an [accepted manuscript](https://drive.google.com/file/d/1MXELrCL2Bgf4-ZaF_EgPUQZFM57sPRLF/view) SHA `a959e039658f8b69bb381ca3ee998f4585e3d64a048654bf27f84fac0be23886`; **different raw byte editions**, no automatic deletion or merge. Smith et al. already study long-run structure, pseudo-stability and multiple ergodic sets under different stochastic adjustment mechanisms.
4. `vythoulkas1990.pdf` is Petros C. Vythoulkas, *A Dynamic Stochastic Assignment Model for the Analysis of General Networks*, Transportation Research B (1990), [00 PDF](https://drive.google.com/file/d/1UZ5AgN43TEiaOCvR_hHP2JXyH_dXO5db/view), in particular day-to-day Markov adjustment as well as joint departure-time/route choices in general networks. It is not a new duplicate of the 2024/2016 two-paper set.

We only read and checked source PDFs. **No raw source bytes have been uploaded to GitHub, and no 00 record was moved or deleted**. Publisher PDF versus author accepted manuscript requires permission/licence and deliberate version policy before any move.

## II. Exact six-actor reference calculation (not novel theory)

Consider six atomic decision makers on parallel routes A/B. Let n be number of A users. At each discrete round every A user independently changes to B with constant probability a; each B user independently changes to A with constant probability b. Define U~Bin(6−n,b), D~Bin(n,a), n'=n+U−D. Exact 7×7 transition probabilities are the convolution of the two binomial laws.

Original Noussair–Qiao congestion cost for occupancy n: C(n)=n²+2(6−n)² = 24+3(n−4)². For any occupancy distribution:
**E[C(N)−24]=3[(E N−4)²+Var(N)]**, which must not be confused with an empirical causal welfare effect.

Take initial n0=4 and constant models S: a=1/10,b=1/5 and F: a=1/4,b=1/2. The invariant probability of an actor being on A equals pi=b/(a+b)=2/3 for BOTH models. Their invariant group distribution is equally **Binomial(6,2/3)**; limiting mean occupancy 4 and expected excess cost 4. Thus neither model beats the other on the stationary mean or distribution. They differ in finite-horizon transients: the signed individual relaxation eigenvalue is lambda=1−a−b = 0.7 for S versus 0.25 for F.

Writing z=lambda^t, at period t the four initially-A agents have P(A)=2/3+z/3 and the two initially-B agents P(A)=2/3−2z/3. Consequently E[n_t]=4 and Var(n_t)=(4/3)(1−z²), so **E[C(n_t)−24]=4(1−lambda^(2t))**. For T rounds t=0,...,T−1 and no discount, **W_T=4T−4(1−lambda^(2T))/(1−lambda²)**.

Results with T=40:
| Model | next-period mean n | next-period variance | expected next excess | 40-period expected cumulative excess |
|---|---:|---:|---:|---:|
| S a=.10,b=.20 | 4 | .68 | 2.04 | 152.1568627451 |
| F a=.25,b=.50 | 4 | 1.25 | 3.75 | 155.7333333333 |

Difference F−S = **+3.5764705882** expected excess cost units across 40 rounds. Both stationary excess costs remain 4. This illustration is highly simplified: no endogenous learning, changing cost feedback, individual cognitive limitations, endogenous information release or randomized update clocks. Do not infer that a real policy should suppress switching or that the comparison is human-data-fitted.

Files:
- [Exact seven-state Ruby](p3/finite_horizon_independent_welfare.rb)
- [70 assertions](p3/test_finite_horizon_independent_welfare.rb)
- [Independent analytic closed form](p3/finite_welfare_closed_form.rb)
- [90 analytic-to-chain parity assertions](p3/test_finite_welfare_closed_form.rb).
Local Ruby 3.3: **8 tests, 160 assertions, 0 failures**. Tests registered in read-only CI; remote GitHub Actions PASS and exact final HEAD execution not yet verified.

## III. Implications for publication and R16B / R17

**Already claimed in predecessor research:** Independent individual-to-macro stochastic routing, Poisson-binomial flows, route-dependent inertia, finite-state stationary distributions, nontrivial day-to-day trajectories, asymptotic stability and the distinction between stationary versus transient effects. Our small exact witness is a transparent implementation/verification negative control, **not a paper-worthy new theorem**.

**Remaining serious question:** Can an information-feasible, mechanism-explicit model trained on individual history and signal/update-clock structure predict externally held-out *joint* opposing flow, occupancy transitions, and cumulative finite-horizon welfare more accurately than strong behaviorally calibrated independent alternatives (especially Qi RDAB-SP, SSM and EWA), and can an intervention distinguish shared latent shocks from direct strategic dependence?

P3-R16B requirements: expand selected n=4 to all current occupancies; replay 24 sessions under original legal information timing and sixfold heldout sessions; fix and score the Qi-compatible attraction/inertia independent baseline and full SSM/EWA prior art; evaluate joint (U,D), unconditional occupancy paths and finite-horizon outcomes; never smuggle future observed cost into individual decisions; nested tune hyperparameters using train sessions only. One-step human-data conditional fits do not authorize 40-step counterfactual causal forecasts without explicit transition-history state consistency.

P3-R17 theory gate: specify information-release and adjustment-clock treatment, prove identifying contrasts on an appropriate history-augmented state space, map observable variables and latent common-shock equivalence; pre-register truly independent data/intervention. Continue difficult micro→macro causal welfare goal rather than pivoting to a trivial prediction leaderboard.

**Scientific verdict:** Important bibliographic custody correction; mathematically correct but known minimal example; empirical, causal and originality claims remain HOLD.
