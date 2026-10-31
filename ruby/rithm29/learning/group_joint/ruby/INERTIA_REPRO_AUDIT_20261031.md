# 2026-10-31 — RITHM 2.9: inertia score audit and session uncertainty

Independent rerun of original stored Ruby inertia_cv.rb on the original 34,560-row session-heldout one_step_predictions.csv discovered **integer division** in the per-fold reporting field:
old: `actual_switch:a.sum{|x|x[:actual_switch]}/a.size`
correct: `actual_switch:a.sum{|x|x[:actual_switch]}.to_f/a.size`.
Six fold displayed values of 1 were false; real fold rates vary, pooled **1.586360398860399**. All six folds were rerun with corrected local code, saved in corrected_scores.csv of associated chat artifact. This column correction does not alter kappa, individual/joint/count predictive probabilities or logloss.

New 24-session paired independent resampling (20,000 draws, deterministic NumPy seed 20261031), based on exact one-step EWA probabilities and six training-fold kappa values:
- mean individual **delta(logloss) = -0.01675994356366941** (inertia minus EWA);
- session-mean bootstrap 95% percentile interval **[-0.02268634,-0.00893755]**;
- **21/24** sessions improve individual logloss.
- 33,696 transition-period individual actions from 5,616 group-periods.
This is an **exploratory cluster interval**; model was already designed using the same observational sample, so it is not an unseen confirmatory result.

Important: the corrected local full runner lives in the chat research artifact pending source transfer to GitHub. Existing GitHub inertia_fit.rb and inertia_calibration.rb are active; never retire these. Main scientific next step: per-session paired joint (U,D) uncertainty + matched-group baseline and nested candidate selection; group covariance alone remains unidentified by aggregate model error. No new human recruitment.
