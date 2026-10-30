# 2026-10-30: New experimental-learning literature, canonicalized

## Source management completed in Google Drive

Ten uploaded articles/working papers were inspected and renamed/moved from `00_INTAKE` to the existing `10_PAPERS` canonical commons. Neither raw PDF bytes nor their Google Drive IDs changed. No monographs among these ten. One original is a **2002 working-paper version**, not the 2008 journal article; another is a textless 24-page JSTOR image scan, first-page identity verified visually but full text not OCR'd.

| Author/year | Source ID | Reading priority |
|---|---|---|
| Ho, Camerer & Chong (2007), *Self-tuning EWA* | 1tk1WDqYoVz1n6_STqae0xGk_jQD1JgH4 | Current lambda/theta/attention, surprise and discount |
| Ho, Camerer & Wang (2002), *Individual Differences in EWA Learning with Partial Payoff Information* [WORKING PAPER] | 1JkW0XzEjMnS_5SuGFJB5UBTTE-5tDsw7 | Partial-feedback counterfactual inference, heterogeneity; not 2008 final |
| Camerer & Ho (1999), *Experience-Weighted Attraction Learning* | 1DHqU4AzmvOOz2VGphQOL3ng3PxmWiyzS | Foundational hybrid reinforcement/belief model |
| Cheung & Friedman (1997), *Individual Learning in Normal Form Games* | 1VD1vjSuAK5EWvlzA0zcA6T_nwJgLRjQW | Short/long-memory heterogeneous belief learning |
| Erev & Barron (2005), *On Adaptation, Maximization, and Reinforcement Learning among Cognitive Strategies* | 1gRLcpzaD6IIQAnfF9R1ih3WX6p64zLkd | Payoff variance and underweighting rare events |
| Hertwig et al (2004), *Decisions from Experience and Effect of Rare Events* | 1l04YLBbRcIv5muT0s288zirnQutNDYQl | Experience/description distinction, small samples |
| Hart & Mas-Colell (2000), *Simple Adaptive Procedure Leading to Correlated Equilibrium* | 1JMOXfjToDriiJnzwzBatEJAB4fz77iX2 | Regret matching benchmark |
| Roth & Erev (1995), *Learning in Extensive-Form Games* | 1xMIwTHYguPIkIwqMcOndSAOlJV98oz7w | Reinforcement empirical foundations |
| Kremer, Mansour & Perry (2014), *Implementing the Wisdom of the Crowd* | 1sBgyVhlwgMQ8_EJk1F87IR79LaewcDiF | Information and exploration incentive; sequential setting |
| Fudenberg & Levine (1993), *Self-Confirming Equilibrium* | 1Gplsqvnn_3TIKVwx5f2_OHoTXHCXN6-7 | 24-page image scan, identity visually verified, full-text reading pending |

Canonical shelf: https://drive.google.com/drive/folders/1D2M4LHcejREhlyp6vTd71xxLLx-6ldUP

## What the originals taught us

Ho et al (2007) deliberately make alternatives with missed rewards salient, and increase forgetting when observed behavior surprises the learner. This suggests separately ablating the change detector, attention, and off-route payoff inference in **existing 24-session heldout CV**, with phase-specific scores.

Ho et al (2002) treat different inference substitutions and individual heterogeneity, but one counterfactual condition is essentially clairvoyant; **it is an oracle bound**, not a participant-feasible learning rule for people receiving only private payoffs.

Cheung & Friedman (1997) directly warn against interpreting a pooled one-parameter representative agent as identical to each subject's learning process. Limited per-individual 40 rounds and sequential group interactions complicate hierarchical inference.

Hertwig et al (2004) and Erev & Barron (2005) connect rare-event underweighting and volatility to finite sample/learning choices, but the six-player route experiment's *random trip values* make raw payoff volatility a mixture of idiosyncratic payoff noise and congestion, so stratified identification is needed.

Hart & Mas-Colell (2000) provide regret matching → correlated equilibrium under their assumptions. Kremer et al (2014) have sequential myopic agents and central info design for exploration, not the same simultaneous endogenous congestion game. These are concept donors, not directly imported theorems.

## Next executable hypotheses
1. Freeze original 24-session splits: EWA phi surprise detector vs constant forgetting; delta salience vs all-counterfactual reinforcement, keeping information filtrations valid.
2. Split by early/full vs late/full: source CV identifies a real sign reversal EWA vs Markov.
3. Move from individual one-step prediction to joint six-person action counts and aggregate welfare; within-group correlated errors and signals should be modeled before claiming collective effects.
4. Model memory/attention costs only with independently discriminating data, avoiding arbitrary compound friction parameters.

This note is supplementary to the real-data experiment record: https://app.notion.com/p/409ef561cf9281f4ab69f336058504d4 .
