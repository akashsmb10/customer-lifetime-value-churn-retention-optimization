"""Generate documentation from executed artifacts, then execute explanatory notebooks."""
from pathlib import Path
import json
import sys
import os
os.environ.setdefault('JUPYTER_RUNTIME_DIR',str(Path(__file__).resolve().parent/'.cache/jupyter'))
os.environ.setdefault('IPYTHONDIR',str(Path(__file__).resolve().parent/'.cache/ipython'))
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
import pandas as pd
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parent

def write(path,text):
    (ROOT/path).write_text(text.strip()+'\n',encoding='utf-8')

def main():
    r=json.loads((ROOT/'artifacts/tables/results.json').read_text());a=r['audit'];h=r['threshold']['horizon_days'];m=r['performance']['selected_test'];v=r['value'];s=r['statistics'];w=r['windows'];sim=pd.read_csv(ROOT/'artifacts/tables/simulation.csv')
    common=f"""Results are generated from `artifacts/tables/results.json`. Monetary amounts are GBP. Observed gross purchases exclude cancellations, returns, nonpositive prices and missing customer identifiers. No experimental intervention response, banking balances, margin or acquisition costs are available.

The prediction estimand is no valid purchase during the next {h} days among customers whose recency is below {h} days at the scoring cutoff. This is operational forward inactivity, not confirmed permanent churn. Survival measures time to the first completed {h}-day gap; a customer can later revive. These related estimands are not identical.
"""
    write('docs/data_dictionary.md',f"""# Data dictionary and source selection
Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), Daqing Chen, DOI 10.24432/C5CG6D, CC BY 4.0. The two sheets contain invoice-product lines for a UK non-store gift retailer, including wholesale customers. Executed dimensions: {a['raw_rows']:,} rows × {a['raw_columns']} columns; dates {a['start']} through {a['end']}.

| Field | Meaning / rule |
|---|---|
| invoice | Purchase invoice identifier; C prefix is cancellation |
| stock | Product identifier; non-merchandise codes may remain, a limitation |
| description | Item text, unused by models |
| quantity | Units; require positive |
| date | Invoice timestamp, local timezone unspecified |
| price | Unit price GBP; require positive |
| customer | Customer identity, require observed identifier |
| country | Customer geography; not a protected-attribute fairness audit |
| revenue | quantity × price; gross positive purchase value |

Candidate evaluation: Online Retail provides only one year, making non-overlapping model and CLV windows restrictive. IBM Telco includes customer identity, tenure and charges but lacks invoice histories for genuine recency, cohorts, interpurchase gaps and transactional CLV. Online Retail II supports all those dimensions over two years, while sacrificing bank-specific products and confirmed churn. No public bank transaction source with comparable documented longitudinal value and churn histories was identified in this review. A bank-like presentation is a transfer discussion, not a bank-data claim.

Archive SHA256: `{a['archive_sha256']}`. Invoice-level key is (customer, invoice). Models do not use identifiers. Clean rows: {a['clean_rows']:,}; orders: {a['orders']:,}; observed customers: {a['customers']:,}.
""")
    write('docs/problem_definition.md',f"""# Business decision
Which currently active customers should receive scarce retention attention when risk and economic exposure differ? Use a reproducible ranking as input to a randomized pilot, not an automatic marketing decision.

{common}

Features use all valid history strictly before each cutoff: recency, invoice frequency, historical monetary total, average invoice value, observed tenure and orders in the preceding 90 days. Retention actions are candidate experiments: high value/high risk receives tailored outreach; high value/low risk receives proactive service; low value/high risk receives low-cost channels; low value/low risk receives routine nurture. Median risk/value split defines descriptive segments, not a decision threshold.
""")
    limitations="""Observed start is left truncated: existing customers can appear as new. Anonymous purchases are excluded and exclusion can bias cohorts and value. Returns cannot be reliably matched, so estimates are gross revenue, not net revenue or profit. Wholesale buyers and extreme purchases distort averages. Seasonality, nonstationary purchase rates, country mix and limited follow-up weaken transferability. A completed inactivity spell is not permanent departure. Calendar-end censoring may be associated with cohort/season; survival groups are descriptive. BG/NBD assumes stationary Poisson purchasing with gamma heterogeneity and dropout after purchases; it cannot represent scheduled contracts or all revivals. Gamma-Gamma assumes positive monetary values and independence between purchase propensity and order value; correlation diagnostics are necessary but do not establish independence. Penalized fits need sensitivity and longer-horizon validation. Risk × value is a proxy: conditional loss severity and uplift are unavailable; multiplying correlated estimates can double-count dropout. Contact effectiveness and margin are assumed. No causal churn drivers, saved revenue, measured uplift or production benefit can be claimed. Banking transfer requires consent, product economics, dormant-account definitions, compliance/fairness review, out-of-time evaluation and randomized treatment data."""
    write('docs/model_scope_and_limitations.md','# Scope and limitations\n'+common+'\n'+limitations)
    write('reports/01_data_audit.md',f"# Executed audit\n```json\n{json.dumps(a,indent=2)}\n```\nCounts of exclusions overlap and must not be added. Exact duplicate lines are removed; identical legitimate repeated item lines may also be removed. Negative quantities/cancellations are audited rather than netted. Dates are parsed from the workbook; there are no null-date rows after cleaning. Dataset timestamps are historical, not impossible relative to extraction. Same invoice/customer lines are aggregated. Outliers are retained; the decision score must be checked for concentration. See schema, missingness, geography and monthly-health tables.\n")
    write('reports/02_churn_definition.md',f"""# Threshold and windows
{common}
The threshold is the ceiling to whole weeks of the 90th percentile of strictly positive consecutive-invoice purchase gaps observed before 2010-06-01. Executed quantiles: `{r['threshold']['gap_quantiles']}`. The chosen threshold is **{h} days**. This captures a long typical repeat-purchase gap without claiming an optimal business rule. Completed gaps underrepresent long censored spells and repeat buyers; sensitivity, not this quantile alone, supports use. The 90th percentile is a transparent design assumption. See `churn_sensitivity.csv` for threshold ±28 days and resulting eligible population/rate changes; populations change as eligibility changes.

Observation history begins with the first dataset purchase and ends strictly before the cutoff. Prediction intervals are [cutoff, cutoff + horizon). The partial last calendar day is excluded from labels. The four windows have a seven-day embargo after each complete prediction interval.
```json
{json.dumps(w,indent=2)}
```
Identity partitions use SHA256 modulo 10 and are disjoint across all four windows. Calendar shift and customer mix both influence holdout differences. No customer ID, post-cutoff behavior, future cohort revenue, survival endpoint or target appears in features. Hyperparameter choices are fixed; model selection uses validation Brier score. Calibration is fitted on a separate later block; its in-sample acceptance rule can be optimistic and is disclosed. Final holdout is not used to choose models/calibration.
""")
    write('reports/03_statistical_analysis.md',f"""# Customer-level statistical findings
H0: pre-cutoff monetary-value distributions are identical for future inactive and purchasing holdout customers. H1: the distributions differ (two-sided Mann-Whitney). Independent customers, ordinal/continuous measurement and exchangeability under H0 are assumed; this is not a causal design. A median interpretation needs similar distribution shapes. Rank-biserial effect is 2U/(n_inactive n_retained)−1, positive for higher inactive values.
```json
{json.dumps(s,indent=2)}
```
Median-difference percentile interval uses 2,000 independent within-group customer bootstrap samples, seed 42. Wilson interval describes the holdout inactivity proportion conditional on this sample, not future stationarity. Statistical evidence does not establish practical profitability: inspect GBP median differences and the effect size. The group label is future behavior; the test is descriptive and never becomes a feature. One prespecified test avoids a fishing expedition; no causal attribution is made.
""")
    health=pd.read_csv(ROOT/'artifacts/tables/customer_health.csv')
    repeat_rate=float((health.orders>1).mean())
    write('reports/07_customer_eda.md',f"""# Customer behavior and revenue health
Observed repeat-invoice customer fraction: {repeat_rate:.6%}. This is the fraction with more than one valid invoice across their available observation history, not a standardized follow-up retention rate. Customer and invoice quantiles are saved in customer_distribution.csv and order_distribution.csv. RFM adds time relative to a specific cutoff; it must not use full-history totals when predicting an earlier period.

Gross revenue shares from top customer fractions: {json.dumps(r['concentration'])}. The actual top-20% share is {r['concentration']['0.2']:.6%}; no forced Pareto rule is needed. The cumulative concentration curve asks whether a few customers dominate commercial exposure. The log-value distribution asks whether a mean-based business case is dominated by extreme customers. Those observations motivate robust summaries and value-model backtests rather than automatic removal of wholesalers. Country totals describe coverage, not country-caused churn. Month-to-month growth combines cohort acquisition, repeat purchases and seasonal effects; it is not causal evidence of marketing performance.

For the holdout, inactive customers' historical monetary median is GBP {s['inactive_median']:.2f} versus GBP {s['retained_median']:.2f} for future purchasers. The negative rank-biserial effect indicates lower historical spending in the inactive group. This does not imply spending prevents inactivity. Lower purchase frequency, shorter available histories and seasonality can confound the association.
""")
    write('reports/08_cohort_analysis.md',"""# Cohort retention and customer value evolution
Acquisition proxy is the first observed purchase month. For cohort c and age k, activity retention R(c,k)=number of distinct cohort customers purchasing in that calendar month / first-observed cohort size. Age zero equals one by construction; later activity may revive, so this matrix is not an absorbing survival curve. Completed observed months without purchases are zero; future ages are NaN. The final partial December is excluded to avoid incomplete-period downward bias.

cohort_counts.csv preserves denominators; cohort_retention.csv preserves rates; cohort_revenue.csv preserves gross value evolution by cohort age. Revenue cells sum customer purchase values, while customer activity counts each identity once per month. SQL monthly retention independently rebuilds the cohort/calendar-age logic. Small late cohorts have short follow-up; apparent retention differences cannot prove acquisition-quality changes. Use mature-cohort comparisons at equal age and standardized calendar follow-up before making a managerial claim.
""")
    write('reports/04_survival_analysis.md',f"""# Survival analysis
S(t)=P(T>t), where T is days from first observed purchase until the first completed {h}-day purchase gap. The hazard h(t)=lim[Δt→0] P(t≤T<t+Δt | T≥t)/Δt. Kaplan-Meier is the product over event times of (1−d_j/n_j). A subsequent revival does not erase the first event. If no qualifying gap completes by the end of observation, duration ends at the administrative cutoff and event=0.
```json
{json.dumps(r['survival'],indent=2)}
```
Curves include Greenwood confidence intervals. Jan-Jun versus Jul-Dec first-observed season is a baseline segment; eventual lifetime spend would introduce post-event information. First-observed customers are not verified new customers. There is a structural event-free interval before the threshold. Cohort length and seasonality limit group comparisons. Cox PH is deliberately omitted: stationarity, left truncation and first-gap events make an explanatory PH fit insufficiently justified here. In a longer bank panel, fit baseline covariates, inspect Schoenfeld residuals, time interactions and PH assumptions, and interpret hazard ratios associationally.
""")
    write('reports/05_clv_analysis.md',f"""# Finite-horizon customer value
BG/NBD uses daily purchase occasions: frequency = repeat purchase days excluding the first day, recency = last minus first day, T = calibration end minus first day. Multiple invoices on one day are combined, matching the day time unit. Gamma-Gamma is fitted only to repeat buyers with positive mean repeat-day value; first occasions are excluded by the summary utility. Zero-repeat buyers receive population-shrunk monetary estimates. Estimated {h}-day future gross revenue = expected future occasions × expected revenue per occasion. The un-discounted finite horizon avoids an unsupported perpetual lifetime claim; the benchmark extrapolates historical invoice intensity and average invoice value.
```json
{json.dumps(v,indent=2)}
```
The Spearman diagnostic is descriptive. A nonzero association weakens independence; statistical nonsignificance would not prove it. Forecast MAE and total forecast/actual are measured on the held-out customer/time block. BG/NBD and Gamma-Gamma are fit using all customers' pre-test histories, which is legitimate unsupervised deployment information, but customer-disjoint supervised evaluation does not imply independent value-model customers. Value predictions are not guaranteed superior to the simple benchmark; report both. No forecast clipping hides tail error.

Numerical implementation: BG/NBD uses a 0.01 penalizer; Gamma-Gamma is unpenalized with q>1 enforced for a finite population mean. A penalized Gamma-Gamma fit reached the q=1 boundary and was rejected. For fitted BG/NBD a<1, the library's log-hypergeometric expectation produced invalid values for some zero-repeat histories. The equivalent finite-horizon expectation is integrated using 96-node Gauss-Jacobi quadrature over posterior dropout probability: conditional on alive, lambda~Gamma(r+x, alpha+T), p~Beta(a,b+x), and E[N(h)|lambda,p]=(1-exp(-lambda*p*h))/p. Multiply the integrated expectation by posterior probability alive. Tests compare it to the closed form in the stable parameter region and check finiteness/monotonicity for low-dropout fits. Saved value models contain parameters rather than unpickleable fitted lambda functions.

Primary model sources: [Fader/Hardie customer-base tutorial](https://www.brucehardie.com/talks/ho_cba_tut_art_14.pdf), [Gamma-Gamma formulation](https://www.brucehardie.com/notes/025/gamma_gamma.pdf).
""")
    selected=sim[(sim.capacity==.1)&(sim.contact_cost==5)&(sim.assumed_success==.05)&(sim.incentive==10)]
    write('reports/06_retention_simulation.md',f"""# Retention policy comparison
Risk-only, value-only, risk × value and random targeting are compared at 5%, 10%, 20% contact capacity. Random results average 200 seeded without-replacement samples. Priority is p(inactivity) × estimated future gross revenue, a value-at-risk proxy, not expected treatment benefit. Under homogeneous treatment success and equal costs, selecting largest scores maximizes the scenario objective for a fixed contact count (exchange argument). With heterogeneous costs/uplift, estimate incremental benefit and solve a knapsack/constrained optimization instead. Capacity is a ceiling: a negative net scenario should recommend no contact rather than force spending.

Scenario retained revenue = sum(priority) × assumed_success. Scenario net contribution = retained revenue × assumed_margin − contacts × (contact_cost + incentive). Incentives are charged to every contact. Margin is 30%; success takes 2%, 5%, 10%; costs GBP 1/5/10; incentives GBP 0/10/25. None are observed. An illustrative 10%-capacity, GBP 5 contact, GBP 10 incentive and 5% effectiveness slice:
```
{selected.to_string(index=False)}
```
Risk × value can win its own arithmetic objective by construction; this is not evidence of actual treatment superiority. Test heterogeneous response with a randomized pilot, intention-to-treat analysis, holdout controls, confidence intervals, incremental margin and customer experience guardrails. Churn risk is not persuadability. Conditional lost value may differ from unconditional BG/NBD forecasts; evaluate risk/value overlap before production.
""")
    write('reports/model_card.md',f"""# Analytics and model card
Intended use: educational retention decision support and experiment design. Non-intended use: production banking, credit decisions, automated customer treatment or causal impact claims.

{common}
Selected model: **{r['model']}**. Histogram gradient boosting is a justified alternative to XGBoost: nonlinear interactions with deterministic settings and no extra boosting dependency. Logistic regression uses log1p and standard scaling fitted on training data. Six features: recency, invoice frequency, gross historical value, AOV, observed tenure, recent order count. Naive benchmark uses the training base rate. Decision metrics at threshold 0.5 are descriptive, not optimized policy thresholds. Average precision is used for PR-AUC.
```json
{json.dumps(r['performance'],indent=2)}
```
Calibration: logistic sigmoid on log odds fitted on the independent calibration block; accepted when that block's Brier improves. Report raw and calibrated holdout scores even when calibration worsens. Quantile reliability curve complements Brier, which combines calibration and discrimination. No hyperparameter search on test data. Model file is trusted local joblib; never load untrusted serialized models.

Global explainability uses held-out permutation importance (10 repeats, Brier degradation). Local explanations replace one feature with its training median on representative highest-risk, highest-priority and borderline customers. Correlated feature perturbations may leave the data manifold. They are raw-model sensitivities, not calibrated additive attributions. SHAP is omitted because transparent model-agnostic perturbations suffice; these are not SHAP values and cannot imply causation.

{limitations}

Monitoring: historical PSI using training deciles, score PSI, base-rate differences, delayed-label Brier and forecast/actual value ratio. A real service also monitors segment counts, realized cohort retention and treatment/control incremental contribution. PSI 0.1/0.25 may be investigation triggers, not statistical pass/fail boundaries. Refit only after diagnosed shift, temporal validation and approval. No production monitoring is claimed.
""")
    sections=['Executive Summary','Business Problem','Dataset','Churn Definition','Customer Analytics','Cohort Retention','Statistical Analysis','Survival Analysis','Churn Prediction','CLV','Retention Prioritization','Business Simulation','Explainability','SQL','Monitoring','Dashboard','Limitations','Reproducibility']
    content=[f"This project turns transaction histories into a ranked retention worklist. It asks who is likely to stop purchasing, how much future gross value they represent, and whether contacting them is worthwhile under explicit budget assumptions. It uses {a['customers']:,} observed retail customers as a transferable analytics case study, with no claim of banking-data validation.",common,f"UCI Online Retail II: {a['raw_rows']:,} × {a['raw_columns']} raw workbook dimensions; {a['clean_rows']:,} valid lines and {a['orders']:,} customer invoices. [Source and dictionary](docs/data_dictionary.md).",f"{h}-day no-purchase prediction among customers with recency below {h}. Threshold uses the pre-training 90th-percentile repeat gap rounded to weeks. Holdout inactivity {w['test']['inactive_rate']:.4%}. [Windows and sensitivity](reports/02_churn_definition.md).",f"Top 20% observed customers contribute {r['concentration']['0.2']:.4%} of gross positive purchase revenue. Monthly health, geography and customer distributions are saved as CSV. No forced 80/20 claim.",'Monthly cohort activity divides active unique customers by first-observed cohort size. Unobserved ages are blank; zero means observed inactivity. Final partial month is excluded. ![Cohorts](artifacts/figures/cohort_retention.png)',f"Mann-Whitney U={s['statistic']:.4f}, p={s['p_value']:.6g}, rank-biserial={s['rank_biserial']:.4f}. [Assumptions, confidence intervals and business interpretation](reports/03_statistical_analysis.md).",'[Kaplan-Meier methodology](reports/04_survival_analysis.md). ![Survival](artifacts/figures/survival.png)',f"Selected {r['model']} by validation Brier; holdout ROC-AUC={m['roc_auc']:.4f}, average precision={m['pr_auc']:.4f}, Brier={m['brier']:.4f}, precision={m['precision']:.4f}, recall={m['recall']:.4f}, F1={m['f1']:.4f}. [Model card](reports/model_card.md). ![Calibration](artifacts/figures/calibration.png)",f"BG/NBD + Gamma-Gamma estimates {h}-day gross future revenue; holdout forecast total GBP {v['predicted_total_test']:.2f}, observed GBP {v['observed_total_test']:.2f}, MAE GBP {v['mae']:.2f}; heuristic MAE GBP {v['simple_mae']:.2f}. [Assumptions and diagnostic](reports/05_clv_analysis.md).",'Median value/risk splits create four profiles; risk × value ranks economic exposure. This is a proxy and not a treatment-effect model.','[Scenario comparisons](reports/06_retention_simulation.md) sweep effectiveness, contact costs, incentives and capacity. Negative scenario contribution means the assumed campaign is unattractive.','Global permutation importance and local median perturbations are saved as tables. They are associations, not causal explanations or SHAP.','Eight DuckDB queries execute against persisted orders and scores. Outputs are saved under artifacts/tables/sql_*.csv.','Historical PSI, score shift, base-rate differences and delayed outcome metrics demonstrate monitoring design; no live service is claimed.','Nine-page Streamlit dashboard loads saved artifacts; no retraining on launch. See commands below.',limitations,"""Windows PowerShell, from the project root:
```powershell
py -3.12 -m venv --without-pip .venv
uv pip install --python .venv\\Scripts\\python.exe -r requirements-lock.txt
.\\.venv\\Scripts\\python.exe run_pipeline.py
.\\.venv\\Scripts\\python.exe finalize.py
.\\.venv\\Scripts\\python.exe -m pytest -q
.\\.venv\\Scripts\\python.exe verify_project.py
.\\.venv\\Scripts\\python.exe -m streamlit run app/app.py
```
The first run downloads the public archive; later runs reuse the checksum-recorded raw input. Pipeline overwrites generated tables/models and recreates SQL tables without consuming previous outputs. Python 3.12 is used; pinned environment is in requirements-lock.txt. Repository folders: config, data/raw, data/processed, notebooks, src, sql, tests, artifacts/tables, artifacts/figures, artifacts/models, reports, docs, app. Full results: artifacts/tables/results.json. Verification evidence: reports/final_audit.md.
"""]
    live_config=ROOT/'config/public_dashboard.json'
    live_notice=''
    if live_config.exists():
        live_url=json.loads(live_config.read_text())['url']
        live_notice=f'**[Open the live dashboard]({live_url})** · [GitHub project](https://github.com/akashsmb10/customer-lifetime-value-churn-retention-optimization)\n\nThe public browser dashboard provides all nine views, customer exploration, and an interactive budget simulator using verified saved artifacts. The original Python Streamlit dashboard remains in `app/app.py`. [Hosting and update instructions](docs/deployment.md).\n\n'
    preview_file=ROOT/'docs/dashboard_preview.md'
    preview=preview_file.read_text(encoding='utf-8').replace('(images/','(docs/images/')+'\n\n' if preview_file.exists() else ''
    write('README.md','# Customer Lifetime Value, Churn & Retention Optimization\n\n'+live_notice+preview+'\n\n'.join('## '+title+'\n\n'+body for title,body in zip(sections,content)))
    questions=[
    ('What is churn here?',f'No valid purchase within {h} days after cutoff among eligible customers; it is inactivity, not permanent exit.'),
    ('How was the threshold chosen?','Pre-training positive interpurchase-gap 90th percentile, rounded to weeks, with ±28-day sensitivity; repeat-buyer and censoring bias are disclosed.'),
    ('What is retention?','Continued activity in an observed period; cohort monthly retention differs from avoiding the first inactivity spell.'),
    ('What is a cohort?','Customers grouped by first observed purchase month; actual acquisition is unknown.'),
    ('What is RFM?','Recency since last invoice, frequency of invoices, monetary gross purchase total, all before cutoff.'),
    ('How do recency definitions differ?','Churn features use cutoff minus last purchase; BG/NBD uses last minus first purchase occasion.'),
    ('What is tenure?','Days from first observed purchase to cutoff, not confirmed relationship age.'),
    ('Why exclude returns?','Unmatched negative lines cannot give reliable net customer economics; gross value limitations must remain explicit.'),
    ('What is CLV?',f'Here it is a {h}-day expected future gross-revenue estimate, not perpetual lifetime profit.'),
    ('Why BG/NBD?','Noncontractual repeat transactions permit a probabilistic purchase/dropout model; stationary-rate assumptions can fail.'),
    ('What does frequency mean in BG/NBD?','Repeat purchase days excluding the first; daily orders are aggregated.'),
    ('What is T?','Days from first purchase to calibration end.'),
    ('What is Gamma-Gamma?','A positive monetary-value model with customer heterogeneity and an independence assumption relative to purchase propensity.'),
    ('How did you test monetary independence?','Spearman rank correlation among repeat purchasers; it diagnoses association but cannot establish independence.'),
    ('Why might CLV estimates be wrong?','Seasonality, wholesalers, heavy tails, dropout misspecification, limited histories, returns and monetary dependence.'),
    ('What is survival analysis?','It models time to the first completed inactivity spell while retaining right-censored customers.'),
    ('What is censoring?','No event is observed by the administrative end; duration is known only to exceed that follow-up.'),
    ('Why survival if you have a classifier?','Survival describes event timing and incomplete follow-up; classification predicts a fixed future window.'),
    ('What is Kaplan-Meier?','Product of conditional survival proportions at event times; intervals use Greenwood uncertainty.'),
    ('What is hazard?','Instantaneous event rate conditional on remaining event-free, not event probability by itself.'),
    ('What is Cox PH?','A proportional baseline hazard model; hazard ratios are associative and require PH diagnostics.'),
    ('Why no Cox model here?','First-gap events, short seasonal panel and left truncation weaken justified interpretation; KM is sufficient for the stated descriptive question.'),
    ('Can a customer revive?','Yes. The first inactivity-spell endpoint persists; monthly cohort activity can rise again.'),
    ('What is logistic regression?','A linear model of log odds; log1p and scaling accommodate skewed pre-cutoff features.'),
    ('Why a tree model?','Histogram gradient boosting captures nonlinear thresholds/interactions as a justified XGBoost alternative.'),
    ('What is XGBoost?','Regularized boosted decision trees; adding it would require the same temporal and identity safeguards, not guarantee improvement.'),
    ('What is ROC-AUC?','Probability a randomly selected inactive customer has a higher score than a purchasing customer.'),
    ('What is PR-AUC here?','Average precision, emphasizing positive-class retrieval and dependent on base rate.'),
    ('Why not accuracy?','Accuracy hides positive-class errors and does not measure probability reliability or economic exposure.'),
    ('What is calibration?','Customers scored near p should show about p inactivity; reliability bins and Brier assess this.'),
    ('What is Brier score?','Mean squared error of probability against binary outcome; lower is better, with both discrimination and calibration components.'),
    ('What is target leakage?','Features derived from future activity, the label window, survival events or future customer value contaminate prediction.'),
    ('What is temporal validation?','Training precedes validation, calibration and test; non-overlapping outcomes and a seven-day embargo limit contamination.'),
    ('How is customer leakage prevented?','Stable SHA256 partitions keep identities disjoint across supervised splits; IDs are not features.'),
    ('Why not random splitting?','It mixes historical regimes and can share customer histories; temporal transfer is the real use case.'),
    ('Can the model prove why customers churn?','No. Permutation importance and perturbations are predictive associations, not causal effects.'),
    ('What is SHAP?','Additive attribution relative to a reference distribution; it is not causal and is not used in this project.'),
    ('Why does high churn probability not automatically justify contact?','Value, costs, persuadability, consent and incremental treatment benefit determine whether contact pays.'),
    ('Why combine churn with CLV?','It introduces economic exposure, but multiplying correlated dropout-aware forecasts can understate lost value; it is a scenario proxy.'),
    ('How are capacity decisions optimized?','Under equal costs and homogeneous assumed effectiveness, choose the highest score; negative net cases justify no contact.'),
    ('What is uplift?','Incremental outcome difference due to treatment, requiring a randomized or justified causal design; unavailable here.'),
    ('What happens when behavior changes?','Monitor feature/score PSI, delayed calibration, cohort activity, value residuals and segment sizes; diagnose before retraining.'),
    ('What does statistical significance mean?','Evidence against the test null conditional on assumptions; it does not demonstrate large economic impact.'),
    ('Why bootstrap customers rather than invoices?','Invoices within a customer are dependent; the customer is the decision and inference unit.'),
    ('How would a real bank differ?','Use balances, fee/interest contribution, multi-product relationships, operational dormant-account definitions, consent and regulatory controls, then test incremental retention.'),
    ('What must you never claim?','Saved revenue, uplift, measured ROI, causal drivers, permanent churn, profit or live production banking effectiveness.'),
    ('Why can risk × value win the simulator?','The simulator objective is defined from that same score; the win is arithmetic, not empirical proof of campaign effectiveness.'),
    ('How would unequal costs change optimization?','Estimate incremental net benefit per action and solve constrained selection or a knapsack with budget/fairness constraints.'),
    ('How are unobserved cohort cells treated?','NaN, not zero; final incomplete month excluded.'),
    ('What are the verified model results?',f"{r['model']}: ROC-AUC {m['roc_auc']:.4f}, average precision {m['pr_auc']:.4f}, Brier {m['brier']:.4f}; inspect full confusion matrix and calibration in the model card.")]
    write('reports/interview_guide.md','# Learn and defend this project\n\nBegin with the business question: prioritize valuable customers at risk, then test whether intervention actually helps. Trace the chain from invoice audit → pre-cutoff RFM → inactivity labels → cohorts and survival → risk probabilities → finite-horizon value → explicit retention scenarios.\n\n'+'\n\n'.join(f'## {i}. {q}\n\n{answer}' for i,(q,answer) in enumerate(questions,1)))
    write('reports/resume_bullets.md',f"""# Customer Lifetime Value, Churn & Retention Optimization
Python | SQL/DuckDB | scikit-learn | Kaplan-Meier | BG/NBD | Gamma-Gamma | Streamlit | pytest

- Analyzed {a['raw_rows']:,} public transaction lines across {a['customers']:,} identified customers, deriving leakage-controlled inactivity labels and cohort retention analyses.
- Evaluated customer-disjoint temporal churn models, achieving holdout ROC-AUC {m['roc_auc']:.3f} and Brier score {m['brier']:.3f}, with separate probability calibration and finite-horizon value backtesting.
- Built a retention decision dashboard and executed {len(r['sql'])} DuckDB queries comparing risk, value and combined targeting under explicitly assumed intervention economics.

Traceability: all counts and metrics originate in artifacts/tables/results.json; this describes analysis and simulated decisions, not realized business uplift.
""")
    notebook_info=[('01_data_audit','Audit invoice lines before customer inference. Missing identifiers and returns create selection and revenue limitations.','missingness'),('02_customer_eda','Ask which customers concentrate gross revenue, and whether that implies concentration of future value.','customer_health'),('03_cohort_retention','Monthly activity is not absorbing churn. Blank cells must not become zero.','cohort_retention'),('04_statistical_analysis','Compare independent customer histories with future behavior; distinguish effects from p-values.','customer_scores'),('05_survival_analysis','First inactivity spell is absorbing for this endpoint, even after revival; censored customers remain in risk sets.','survival_customers'),('06_churn_modeling','Temporal windows and disjoint identities are more relevant than a random split. Read raw and calibrated holdout scores.','calibration'),('07_clv_modeling','Check finite-horizon forecasts against observed revenue and a simple extrapolation; assumptions may fail.','customer_scores'),('08_retention_prioritization','Probability × future gross revenue describes economic exposure, not causal treatment benefit.','segments'),('09_business_simulation','All success, costs and margins are assumptions; a ranking win is not proof of saved revenue.','simulation')]
    for name,narrative,table in notebook_info:
        nb=nbf.v4.new_notebook();nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}
        nb.cells=[nbf.v4.new_markdown_cell(f'# {name.replace("_"," ")}\n\n{narrative}\n\nReusable calculations live in src/ and run_pipeline.py. This notebook reads executed artifacts so analysis cannot silently retrain or leak future data.'),nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display\nroot=Path.cwd().parent if Path.cwd().name=='notebooks' else Path.cwd()\nresults=json.loads((root/'artifacts/tables/results.json').read_text())"),nbf.v4.new_code_cell(f"data=pd.read_csv(root/'artifacts/tables/{table}.csv')\ndisplay(data.head(12))\ndisplay(data.describe(include='all').T)"),nbf.v4.new_markdown_cell('Interpretation: consult the corresponding report for mathematical definitions, executed estimates and their limits. Never turn an assumed campaign response into an observed result.')]
        if name=='04_statistical_analysis':nb.cells.append(nbf.v4.new_code_cell("display(results['statistics'])"))
        if name=='06_churn_modeling':nb.cells.append(nbf.v4.new_code_cell("display(results['performance'])"))
        if name=='07_clv_modeling':nb.cells.append(nbf.v4.new_code_cell("display(results['value'])"))
        report={'01_data_audit':'01_data_audit.md','02_customer_eda':'07_customer_eda.md','03_cohort_retention':'08_cohort_analysis.md','04_statistical_analysis':'03_statistical_analysis.md','05_survival_analysis':'04_survival_analysis.md','06_churn_modeling':'model_card.md','07_clv_modeling':'05_clv_analysis.md','08_retention_prioritization':'06_retention_simulation.md','09_business_simulation':'06_retention_simulation.md'}[name]
        nb.cells.append(nbf.v4.new_markdown_cell((ROOT/'reports'/report).read_text(encoding='utf-8')))
        path=ROOT/'notebooks'/f'{name}.ipynb'
        # Kernel launch uses this environment explicitly, avoiding the unrelated system Python.
        from jupyter_client import KernelManager
        km=KernelManager(kernel_name='python3')
        km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        NotebookClient(nb,timeout=120,km=km,resources={'metadata':{'path':str(ROOT)}}).execute(cleanup_kc=True)
        nbf.write(nb,path);print(f'Executed {path.name}',flush=True)

if __name__=='__main__':main()
