# Falsifiable source-only directions
1. Fit empirical group-level count base distribution with identical 6-fold heldout splits, not LOSO, so evaluation is paired.
2. Calibrate individual probabilities on training sessions only, then combine, to separate marginal miscalibration from within-group dependence.
3. Model joint route counts with explicit shared latent group shock or exchangeable correlated Bernoulli law; estimate group-level log loss with train-only parameters.
4. Compare observed simultaneous switches conditional on past-period route counts with independent predictive switching distribution; no current-period information leakage.
5. Test individual EWA chosen-only ablation after combining its six predictions, rather than assuming its improved individual log loss improves group score.
6. All experiments must use original existing data only: NO new human recruitment or experiments.
