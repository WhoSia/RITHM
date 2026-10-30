# Erev & Roth (2014) → RITHM: sample size, rare events and endogenous learning

Original paper: Erev, I. & Roth, A. E. (2014), *Maximization, Learning, and Economic Behavior*, PNAS 111(Suppl. 3):10818–10825. DOI: https://doi.org/10.1073/pnas.1402846111. Original PDF inspected and canonicalized in Drive, file ID `1cjtLOwTCFBF3-Brm_nw33f0zBimH6Nfn`, https://drive.google.com/file/d/1cjtLOwTCFBF3-Brm_nw33f0zBimH6Nfn/view

## Read from primary source

The paper describes learning toward maximization as strongly dependent on the distribution of feedback: higher mean payoff is not enough if the superior action is not rewarded *most of the time*. Its “Reliance on Small Samples” section compares a sample of 5 past trials drawn with replacement and a sample of 9 or less, and connects single-draw samples to probability matching. Its “Effect of Limited Feedback” section discusses missing foregone payoffs and the hot-stove effect. Sample dependence is compatible with either cognitive economy or adaptation in nonstationary settings; the article does not directly identify these motives in the six-player traffic experiment.

## Independent formal result

For event probability r in IID with-replacement sampling, the chance of seeing it at least once in q draws is f(q)=1-(1-r)^q. At r=0.1:
- fixed q=5: f(5)=0.40951;
- uniform q∈{1,...,9}: E[f(q)]=0.387420489; E[q]=5.
- f(q+1)-f(q)=r(1-r)^q decreasing in q: variable q does **not** increase exposure to rare events at equal expected sample count; concavity gives f(Eq)≥E[f(q)].

This calculation provides a sharp research distinction, not observed choice evidence. In the 6-player congestion game holding opponents fixed, for other-A-count m, A cost m+1 and alternative B cost 2(6-m); A wins for m≤3, B for m≥4. The uninformed player may not distinguish route-relevant other counts from own payoff alone because travel value varies.

## Code and next empirical test

GitHub commit `c1eae1c06cec546b967d84153d51976bc34e9216`: in SmallSample initializer, draw q_i once for the person; do not re-draw every choose() period. Source: Noussair–Qiao Online Appendices B.1. Ruby regression suite: 6 tests, 24 assertions, passed.

Existing SSM empirical comparisons have not been rerun with this new generator. The next meaningful step is a participant-persistent latent-q *sequence* likelihood, accounting for feedback filtration; and discrimination between EWA attention-driven forgetting, SSM small samples and simple switching inertia in held-out sessions, including late Full and early Full exceptions.

Notion full notes: https://app.notion.com/p/409ef561cf9281f4ab69f336058504d4
