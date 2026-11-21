# RITHM-2.10 R66-T13 — Friction Taxonomy, Attention–Clock Welfare Reversal & Identifiability

**2026-11-22; MAIN branch only; native Ruby 3.3 Rational arithmetic. Source-free synthetic model, not a new human experiment.**

## Scientific correction

The behavioral label "inertia / laziness" conflates at least seven distinct generative mechanisms: (1) physical resource switching costs, (2) subjective private payoff-improvement thresholds, (3) limited attentional processing, (4) default/status-quo bias even without costs, (5) dynamic habit/tenure, (6) loss avoidance or ambiguous payoff beliefs, and (7) strategic waiting for others' revisions. A homogeneous no-switch probability does not identify any one mechanism. Existing T7–T12 research too often emphasizes joint-switch covariance without modeling what creates an actor's delay.

**Already held primary sources**, read as rivals: [Sims(2003)](https://drive.google.com/file/d/1G7Zon3d0MREDzrpKu5QfH2Hqq8i8VKQg/view), [Caballero & Engel(1993)](https://drive.google.com/file/d/18SaVLo-ZIewWUrPOA0Ul4EeHbTkOwNXN/view), [Klemperer(1987)](https://drive.google.com/file/d/1olKjQAlXObCgxna5mI-HWksGpuIHwFLa/view), [Samuelson & Zeckhauser(1988)](https://drive.google.com/file/d/14yL8dMpVKaIGZYFXIOMD9g4cPDsKlyc2/view), [Laibson(1997)](https://drive.google.com/file/d/1eDLIBZWSply4BoFa-aVJnOSRPo0tzfrM/view), [O'Donoghue & Rabin(1999)](https://drive.google.com/file/d/1UPdI1PUkuquXT_aqb0Lo26LbdnVYEBfh/view), [Gabaix(2014)](https://drive.google.com/file/d/1x5mYXfjYOeh55ecQ7iYFiHKojabj1gMY/view), [Mankiw(1985)](https://drive.google.com/file/d/1026oL54hoOGsumjfsrl7Vg1yYVGFN6cj/view). Avoid wasting work on duplicating existing PDFs.

## Exact microscopic model

Six actors and two routes have original cost c_A(n)=n, c_B(n_B)=2 n_B and social excess L(n)=3(n-4)^2. A single actor's myopic private benefit from changing, holding other revisions fixed, is g_A=3n-14 if currently on A and g_B=11-3n if on B.

The added **hypothetical** behavioral revision probability given a revision *opportunity* is:
`r(g)=q*(g+b>kappa ? 2/5 : 1/50)+(1-q)/50`,
where q is an exogenous attention probability, kappa the subjective minimum expected private gain to justify switching, and b a placeholder payoff bias. This is not Sims-style optimized capacity allocation, structural prospect theory, or estimated human behavior.

Three action-*opportunity* schedules have the same per-actor eligibility probability 1/2 at every occupancy: common six-or-zero, six IID Bernoulli, and exactly three uniformly chosen. Eligibility pair covariance +1/4, 0, -1/20. Distinct from actually receiving information or changing routes. Actual social physical switching expense is a **different parameter** f multiplying expected realized gross switches; do not count kappa as a resource expense.

## Exact forty-period policy-ranking counterexamples

Initial A occupancy 4, H=40; entries are cumulative social congestion excess (excluding 24 per period), *before* any real fee f. Exact Ruby Rational computations, rounded for readability.

| Attention q | Private threshold kappa | Common | IID | Uniform fixed-three | Best |
|---|---:|---:|---:|---:|---|
| 1 | 0 | 43.19302430 | 18.25763949 | **15.96387363** | fixed-three |
| 1/2 | 0 | 31.88816280 | 24.09233699 | **22.97059218** | fixed-three |
| 1/2 | 2 | **64.56300042** | 64.70483377 | 64.72890240 | common |
| 0 | 0 | **103.17384461** | 103.35591096 | 103.39212863 | common |
| 1 | 5 | **91.68014060** | 93.15427260 | 93.36495014 | common |

This directly falsifies **universal fixed-three schedule dominance under every cognitive friction assumption** in the T12 rule family. Importantly, the no-attention limit still allows 1/50 lapse errors, and all three schedules then yield identical expected 2.34 gross changes over 39 transitions but **different congestion** through simultaneous error cancellation and feedback.

**New interaction:** increasing q from 1/2 to 1, at kappa=0, **worsens** the common-clock social loss by about +11.305 while **improving** IID by -5.835 and fixed-three by -7.007. More cognitive attention is not universally higher *aggregate* welfare in this toy game. It is NOT evidence that more information is harmful to actual participants.

## Identification counterexample and prospective instrument

For a strictly positive private benefit, zero lapse, and conditional response r=2/5, observed switch probability is p=theta*q*r, where theta is the revision opportunity probability. (theta,q)=(1/2,1/2) and (1/4,1) both imply the identical p=1/10. Thus individual switch observations cannot identify opportunity versus attentional engagement without separate exposure or a valid randomized instrument. A hypothetical controlled design with *known* theta, r and lapse permits q=(p/theta-lapse)/(r-lapse), only when theta>0 and r != lapse. Neither real q nor real threshold is estimated from the old 24 sessions.

## Prior art, challenges, methodological gating

- These exact calculations use elementary finite Markov chains and rational expected values; they do **not** establish mathematical novelty relative to Caballero–Engel (state-dependent hazards), Sims / Gabaix / Matějka–McKay (attention), or Klemperer (switching costs). Do not call them a newly discovered universal theorem.
- Habit/tenure cannot in general be faithfully represented by a 7-occupancy-state Markov chain; persistent labelled actor types require at least actor-labelled route history and additional state.
- Correctly identifying a causal attention effect requires observing or manipulating attention separately from opportunity and price, with a new independent cohort. Group-level randomization / prospective outcome registration is necessary for human policy claims.
- Avoid treating repeated LOSO results on the same original 24 sessions as an independent validation. The source-free T13 theoretical models use no participant rows, so they make no new empirical causal claims.
- **Research director next:** design competing 64-labelled-state (plus habit state) models with a genuine negative control, distinguish structural adjustment vs information acquisition timing, and identify a prospectively testable predictive restriction. The stronger scientific target is **conditional amplification versus damping**, not unconditional friction harms welfare.

## Literature custody and reading

A fresh candidate inventory contains **10 targeted unheld PDF candidates**: Guo 2026 from the existing 55-paper register and nine new candidates from direct publisher/university sources: Caballero–Engel 1993 *Heterogeneity and Output Fluctuations*; Matějka–McKay 2015 *Rational Inattention to Discrete Choices*; Reis 2006 *Inattentive Producers*; Woodford 2009 *Information-Constrained State-Dependent Pricing*; Calvo 1983; Kőszegi–Rabin 2006; Chetty–Looney–Kroft 2009; DellaVigna 2009; Carroll–Overland–Weil 2000. These are title/author based Drive misses, **not proof of absence after byte-census**. Availability of a public author manuscript is sufficient for research; no reason to insist on final published PDF. The nine held comparator papers and their exact Drive IDs are in the accompanying spreadsheet.

## Reproduction

Native Ruby source in `ruby/rithm210/p3/r66_t13_*.rb`; Minitest `test_r66_t13_*.rb`. Local Ruby 3.3.8: **26 runs / 53 assertions / 0 failures**. Execute `ruby -I. -e 'Dir["test_r66_t13_*.rb"].sort.each { |f| require_relative f }'`. Recompute five cells with `ruby r66_t13_counterexamples.rb`. Remote CI requires separate verification. All code committed to **main** under human actor WhoSia. No GitHub Actions bot authorship.
