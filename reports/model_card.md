# Analytics and model card
Intended use: educational retention decision support and experiment design. Non-intended use: production banking, credit decisions, automated customer treatment or causal impact claims.

Results are generated from `artifacts/tables/results.json`. Monetary amounts are GBP. Observed gross purchases exclude cancellations, returns, nonpositive prices and missing customer identifiers. No experimental intervention response, banking balances, margin or acquisition costs are available.

The prediction estimand is no valid purchase during the next 77 days among customers whose recency is below 77 days at the scoring cutoff. This is operational forward inactivity, not confirmed permanent churn. Survival measures time to the first completed 77-day gap; a customer can later revive. These related estimands are not identical.

Selected model: **logistic**. Histogram gradient boosting is a justified alternative to XGBoost: nonlinear interactions with deterministic settings and no extra boosting dependency. Logistic regression uses log1p and standard scaling fitted on training data. Six features: recency, invoice frequency, gross historical value, AOV, observed tenure, recent order count. Naive benchmark uses the training base rate. Decision metrics at threshold 0.5 are descriptive, not optimized policy thresholds. Average precision is used for PR-AUC.
```json
{
  "validation": {
    "logistic": {
      "roc_auc": 0.7230609057782404,
      "pr_auc": 0.5814342603399315,
      "precision": 0.55,
      "recall": 0.4852941176470588,
      "f1": 0.515625,
      "brier": 0.2053640529250341,
      "log_loss": 0.5900042521752229,
      "confusion_matrix": [
        [
          86,
          27
        ],
        [
          35,
          33
        ]
      ]
    },
    "gradient_boosting": {
      "roc_auc": 0.7335372201978136,
      "pr_auc": 0.6190140472974868,
      "precision": 0.5441176470588235,
      "recall": 0.5441176470588235,
      "f1": 0.5441176470588235,
      "brier": 0.20849756886700307,
      "log_loss": 0.6016070393566807,
      "confusion_matrix": [
        [
          82,
          31
        ],
        [
          31,
          37
        ]
      ]
    }
  },
  "base_rate": {
    "roc_auc": 0.5,
    "pr_auc": 0.5179063360881543,
    "precision": 0.0,
    "recall": 0.0,
    "f1": 0.0,
    "brier": 0.2514939266716296,
    "log_loss": 0.6961379627963018,
    "confusion_matrix": [
      [
        175,
        0
      ],
      [
        188,
        0
      ]
    ]
  },
  "raw_test": {
    "roc_auc": 0.7603039513677812,
    "pr_auc": 0.7543165741244132,
    "precision": 0.7575757575757576,
    "recall": 0.39893617021276595,
    "f1": 0.5226480836236934,
    "brier": 0.23371936167871699,
    "log_loss": 0.6653324333709372,
    "confusion_matrix": [
      [
        151,
        24
      ],
      [
        113,
        75
      ]
    ]
  },
  "calibrated_test": {
    "roc_auc": 0.7603039513677812,
    "pr_auc": 0.7543165741244132,
    "precision": 0.7058823529411765,
    "recall": 0.6382978723404256,
    "f1": 0.6703910614525139,
    "brier": 0.2020210138043872,
    "log_loss": 0.5851394494575433,
    "confusion_matrix": [
      [
        125,
        50
      ],
      [
        68,
        120
      ]
    ]
  },
  "selected_test": {
    "roc_auc": 0.7603039513677812,
    "pr_auc": 0.7543165741244132,
    "precision": 0.7058823529411765,
    "recall": 0.6382978723404256,
    "f1": 0.6703910614525139,
    "brier": 0.2020210138043872,
    "log_loss": 0.5851394494575433,
    "confusion_matrix": [
      [
        125,
        50
      ],
      [
        68,
        120
      ]
    ]
  },
  "calibration_used": true
}
```
Calibration: logistic sigmoid on log odds fitted on the independent calibration block; accepted when that block's Brier improves. Report raw and calibrated holdout scores even when calibration worsens. Quantile reliability curve complements Brier, which combines calibration and discrimination. No hyperparameter search on test data. Model file is trusted local joblib; never load untrusted serialized models.

Global explainability uses held-out permutation importance (10 repeats, Brier degradation). Local explanations replace one feature with its training median on representative highest-risk, highest-priority and borderline customers. Correlated feature perturbations may leave the data manifold. They are raw-model sensitivities, not calibrated additive attributions. SHAP is omitted because transparent model-agnostic perturbations suffice; these are not SHAP values and cannot imply causation.

Observed start is left truncated: existing customers can appear as new. Anonymous purchases are excluded and exclusion can bias cohorts and value. Returns cannot be reliably matched, so estimates are gross revenue, not net revenue or profit. Wholesale buyers and extreme purchases distort averages. Seasonality, nonstationary purchase rates, country mix and limited follow-up weaken transferability. A completed inactivity spell is not permanent departure. Calendar-end censoring may be associated with cohort/season; survival groups are descriptive. BG/NBD assumes stationary Poisson purchasing with gamma heterogeneity and dropout after purchases; it cannot represent scheduled contracts or all revivals. Gamma-Gamma assumes positive monetary values and independence between purchase propensity and order value; correlation diagnostics are necessary but do not establish independence. Penalized fits need sensitivity and longer-horizon validation. Risk × value is a proxy: conditional loss severity and uplift are unavailable; multiplying correlated estimates can double-count dropout. Contact effectiveness and margin are assumed. No causal churn drivers, saved revenue, measured uplift or production benefit can be claimed. Banking transfer requires consent, product economics, dormant-account definitions, compliance/fairness review, out-of-time evaluation and randomized treatment data.

Monitoring: historical PSI using training deciles, score PSI, base-rate differences, delayed-label Brier and forecast/actual value ratio. A real service also monitors segment counts, realized cohort retention and treatment/control incremental contribution. PSI 0.1/0.25 may be investigation triggers, not statistical pass/fail boundaries. Refit only after diagnosed shift, temporal validation and approval. No production monitoring is claimed.
