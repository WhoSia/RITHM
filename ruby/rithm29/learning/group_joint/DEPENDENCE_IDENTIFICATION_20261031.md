# Identification audit: conditional dependence versus marginal calibration

For six binary A-route choices X_i and N=sum_i X_i, the exact cost identity is C(N)=4+(N-4)^2/2. Define true individual conditional means m_i=E[X_i|H], and predictor p_i. For the **true** joint distribution,
E[C(N)|H]=4+((sum_i m_i-4)^2+sum_i m_i(1-m_i)+2 sum_{i<j}Cov(X_i,X_j|H))/2.
For an independent product model using the *same true margins* m_i, the difference is exactly sum_{i<j}Cov(X_i,X_j|H). If the product uses **estimated** p_i instead, the discrepancy also contains a marginal error:
E[C|H]-E_ind,p[C|H]
= sum_{i<j}Cov(X_i,X_j|H)
 + 1/2 { (sum m_i-4)^2-(sum p_i-4)^2
         + sum m_i(1-m_i)-sum p_i(1-p_i) }.
This is the missing identification check: joint mean-cost disagreement alone does **not** establish correlated actions, because imperfect p_i may account for it.

Observational diagnostics without new human participation: score group count distributions on existing 5,760 group-periods; compare individual held-out calibration curves and predicted-vs-actual switching conditional on previous action; fit nuisance probability calibrators on TRAINING sessions only; report session-clustered uncertainty. Unobserved common context and endogenous congestion prevent causal inference solely from residual covariance.

Research OS source housekeeping: ebook EPUBs are legitimate book holdings, not unconditionally 'edition HOLD'. Keith Payne (2017) *The Broken Ladder* was validated via ZIP OPF title/author/ISBN and moved into `11_BOOKS` in its original EPUB form. Byte duplicate holds and unknown-edition sources should not be silently removed without verification.
