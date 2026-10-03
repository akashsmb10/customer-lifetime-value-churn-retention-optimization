# Finite-horizon customer value
BG/NBD uses daily purchase occasions: frequency = repeat purchase days excluding the first day, recency = last minus first day, T = calibration end minus first day. Multiple invoices on one day are combined, matching the day time unit. Gamma-Gamma is fitted only to repeat buyers with positive mean repeat-day value; first occasions are excluded by the summary utility. Zero-repeat buyers receive population-shrunk monetary estimates. Estimated 77-day future gross revenue = expected future occasions × expected revenue per occasion. The un-discounted finite horizon avoids an unsupported perpetual lifetime claim; the benchmark extrapolates historical invoice intensity and average invoice value.
```json
{
  "spearman_r": 0.22243985125024268,
  "p_value": 3.770631747033588e-34,
  "repeat_customers": 2928,
  "bg_parameters": {
    "r": 0.7385453171127513,
    "alpha": 68.39415707791873,
    "a": 0.009200399700005092,
    "b": 0.30594446535083714
  },
  "gg_parameters": {
    "p": 2.2561922836607904,
    "q": 3.5117641147880474,
    "v": 463.67818800651486
  },
  "horizon_days": 77,
  "predicted_total_test": 227263.28698695483,
  "observed_total_test": 167977.61,
  "mae": 420.38084472936595,
  "simple_mae": 744.9106912638299,
  "median_prediction": 327.4864038874745
}
```
The Spearman diagnostic is descriptive. A nonzero association weakens independence; statistical nonsignificance would not prove it. Forecast MAE and total forecast/actual are measured on the held-out customer/time block. BG/NBD and Gamma-Gamma are fit using all customers' pre-test histories, which is legitimate unsupervised deployment information, but customer-disjoint supervised evaluation does not imply independent value-model customers. Value predictions are not guaranteed superior to the simple benchmark; report both. No forecast clipping hides tail error.

Numerical implementation: BG/NBD uses a 0.01 penalizer; Gamma-Gamma is unpenalized with q>1 enforced for a finite population mean. A penalized Gamma-Gamma fit reached the q=1 boundary and was rejected. For fitted BG/NBD a<1, the library's log-hypergeometric expectation produced invalid values for some zero-repeat histories. The equivalent finite-horizon expectation is integrated using 96-node Gauss-Jacobi quadrature over posterior dropout probability: conditional on alive, lambda~Gamma(r+x, alpha+T), p~Beta(a,b+x), and E[N(h)|lambda,p]=(1-exp(-lambda*p*h))/p. Multiply the integrated expectation by posterior probability alive. Tests compare it to the closed form in the stable parameter region and check finiteness/monotonicity for low-dropout fits. Saved value models contain parameters rather than unpickleable fitted lambda functions.

Primary model sources: [Fader/Hardie customer-base tutorial](https://www.brucehardie.com/talks/ho_cba_tut_art_14.pdf), [Gamma-Gamma formulation](https://www.brucehardie.com/notes/025/gamma_gamma.pdf).
