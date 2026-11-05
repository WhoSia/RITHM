# P3-R9 Literature Note C — Benaïm, Hofbauer & Sorin (2005)

**Verified primary PDF:** [Stochastic Approximations and Differential Inclusions, SIAM Journal on Control and Optimization 44(1), 328–348, DOI 10.1137/S0363012904439301](https://drive.google.com/file/d/1eLf0Mzdi580E1Zb1zgtUUWDsVYzjwwME/view).

## Exact technical claim
The authors study the set-valued dynamical system dx/dt ∈ F(x), with a closed graph, nonempty compact convex values, and a linear growth bound (Hypothesis 1.1). Theorem 3.6 states that the limit set of a **bounded perturbed solution** to the differential inclusion is **internally chain transitive**. This is much weaker than generic convergence to a unique Nash equilibrium. Fictitious play and approachability appear as applications under stated hypotheses.

## Applicability and danger
RITHM's 40-period SSM5 uses fixed sample size q=5 and sampling noise; its action process need not be an asymptotic pseudo-trajectory of any differential inclusion without an explicitly proved vanishing-error/step-size regime. A small learning rate approximation cannot be assumed uniformly accurate in the finite, stochastic, fixed-six setting.

## Research program
For a candidate micro update x_{t+1}-x_t=gamma_t(F(x_t)+noise_t), spell out (a) the state vector including all private belief histories, (b) measurability to each actor's information, (c) compactness and boundedness, (d) step-size conditions, (e) martingale or summable disturbance control, (f) whether the expected drift is single- or set-valued. Only after those conditions are proved may Theorem 3.6 restrict the long-run limit set. Separately compute finite-40-period welfare; an asymptotic result does not directly answer the empirical task.
