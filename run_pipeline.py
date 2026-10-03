"""Deterministic, artifact-producing portfolio analysis. Run from repository root."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
os.environ.setdefault('OMP_NUM_THREADS','1')
import json
import hashlib
import warnings
import sys
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import duckdb
from scipy import stats
from lifelines import KaplanMeierFitter
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from src.data import load_data, clean_data
from src.features import FEATURES
from src.churn import labeled_snapshot
from src.survival import survival_dataset
from src.clv import estimate_value
from src.modeling import fit_models
from src.prioritization import prioritize, simulate
from src.monitoring import psi
from src.validation import validate_snapshot

ROOT = Path(__file__).resolve().parent
TABLE = ROOT/'artifacts/tables'
FIG = ROOT/'artifacts/figures'

def save_table(frame,name,index=False):
    frame.to_csv(TABLE/f'{name}.csv',index=index)

def figure(name):
    plt.tight_layout()
    plt.savefig(FIG/f'{name}.png',dpi=150)
    plt.close()

def main():
    if '--clean' in sys.argv:
        for name in ['artifacts/tables','artifacts/figures','artifacts/models','data/processed']:
            target=(ROOT/name).resolve()
            if ROOT.resolve() not in target.parents:
                raise ValueError('Clean target outside project')
            if target.exists():shutil.rmtree(target)
    for folder in ['data/processed','artifacts/tables','artifacts/figures','artifacts/models','reports','docs','config','sql','notebooks','app','tests']:
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    print('Loading public workbook',flush=True)
    raw, digest = load_data(ROOT)
    lines,orders = clean_data(raw)
    end = orders.date.max().normalize() # exclude partial final day from label/survival horizons
    audit = {'raw_rows':len(raw),'raw_columns':len(raw.columns),'duplicates':int(raw.duplicated().sum()),'missing_customer_rows':int(raw.customer.isna().sum()),'negative_quantity_rows':int((raw.quantity<0).sum()),'nonpositive_price_rows':int((raw.price<=0).sum()),'cancellation_rows':int(raw.invoice.astype(str).str.upper().str.startswith('C').sum()),'clean_rows':len(lines),'orders':len(orders),'customers':orders.customer.nunique(),'start':str(orders.date.min()),'end':str(orders.date.max()),'archive_sha256':digest,'missingness':raw.isna().sum().to_dict(),'gross_positive_revenue':float(lines.revenue.sum())}
    audit.update({'outside_documented_date_rows':int(((raw.date<pd.Timestamp('2009-12-01'))|(raw.date>=pd.Timestamp('2011-12-10'))).sum()),'invoice_ids_multiple_customers':int((orders.groupby('invoice').customer.nunique()>1).sum()),'positive_revenue_p99_invoice':float(orders.revenue.quantile(.99))})
    orders.to_parquet(ROOT/'data/processed/orders.parquet',index=False)
    save_table(raw.dtypes.astype(str).rename('dtype').to_frame(),'schema',True)
    save_table(raw.isna().mean().rename('missing_fraction').to_frame(),'missingness',True)
    # Threshold selected only from pre-training history; quarter-like horizon rounded to full weeks.
    discovery = orders[orders.date<pd.Timestamp('2010-06-01')].sort_values(['customer','date'])
    gaps = discovery.groupby('customer').date.diff().dt.total_seconds().div(86400)
    gaps = gaps[gaps>0]
    quantiles = gaps.quantile([.5,.75,.9,.95])
    horizon = int(np.ceil(quantiles.loc[.9]/7)*7)
    cutoff_train = pd.Timestamp('2010-06-01')
    cutoff_validation = cutoff_train + pd.Timedelta(days=horizon+7)
    cutoff_calibration = cutoff_validation + pd.Timedelta(days=horizon+7)
    cutoff_test = cutoff_calibration + pd.Timedelta(days=horizon+7)
    if cutoff_test+pd.Timedelta(days=horizon)>end:
        raise ValueError('Selected horizon does not permit four non-overlapping windows')
    # Stable identity partitions: unseen customers across model selection, calibration and test.
    def partition(customer):
        return int(hashlib.sha256(str(customer).encode()).hexdigest()[:8],16)%10
    snapshots = []
    for cutoff,allowed in [(cutoff_train,range(6)),(cutoff_validation,[6]),(cutoff_calibration,[7]),(cutoff_test,[8,9])]:
        f = labeled_snapshot(orders,cutoff,horizon,end)
        f = f[[partition(c) in allowed for c in f.index]]
        validate_snapshot(f,cutoff)
        snapshots.append(f)
    train,val,cal,test = snapshots
    for name,f in zip(['train','validation','calibration','test'],snapshots):
        save_table(f.reset_index(),'snapshot_'+name)
    assert not any(set(a.index)&set(b.index) for i,a in enumerate(snapshots) for b in snapshots[i+1:])
    sensitivity = []
    for h in sorted(set([max(7,horizon-28),horizon,horizon+28])):
        f = labeled_snapshot(orders,cutoff_test,h,end)
        sensitivity.append({'horizon':h,'eligible':len(f),'inactive_rate':f.inactive.mean()})
    save_table(pd.DataFrame(sensitivity),'churn_sensitivity')
    print(f'Model windows: horizon={horizon}; sizes={[len(s) for s in snapshots]}',flush=True)
    bundle,p,performance = fit_models(train,val,cal,test)
    joblib.dump(bundle,ROOT/'artifacts/models/churn.joblib')
    test = test.copy()
    test['risk'] = p
    value,bg,gg,value_diagnostics = estimate_value(orders,cutoff_test,horizon)
    joblib.dump({'bg_parameters':bg.params_.to_dict(),'gg_parameters':gg.params_.to_dict(),'bg_penalizer':0.01,'gg_penalizer':0.0},ROOT/'artifacts/models/value.joblib')
    test = test.join(value[['future_revenue','simple_revenue','expected_purchases','expected_order_value']])
    actual = orders[(orders.date>=cutoff_test)&(orders.date<cutoff_test+pd.Timedelta(days=horizon))].groupby('customer').revenue.sum()
    test['observed_future_revenue'] = actual.reindex(test.index,fill_value=0)
    value_diagnostics.update({'horizon_days':horizon,'predicted_total_test':float(test.future_revenue.sum()),'observed_total_test':float(test.observed_future_revenue.sum()),'mae':float(abs(test.future_revenue-test.observed_future_revenue).mean()),'simple_mae':float(abs(test.simple_revenue-test.observed_future_revenue).mean()),'median_prediction':float(test.future_revenue.median())})
    ranked = prioritize(test)
    save_table(ranked.reset_index(),'customer_scores')
    save_table(simulate(ranked),'simulation')
    save_table(ranked.groupby('segment').agg(customers=('risk','size'),mean_risk=('risk','mean'),predicted_revenue=('future_revenue','sum'),observed_future_revenue=('observed_future_revenue','sum')),'segments',True)
    all_rfm = orders.groupby('customer').agg(revenue=('revenue','sum'),orders=('invoice','size'))
    concentration = {str(q):float(all_rfm.nlargest(int(np.ceil(len(all_rfm)*q)),'revenue').revenue.sum()/all_rfm.revenue.sum()) for q in [.01,.05,.1,.2]}
    save_table(all_rfm.reset_index(),'customer_health')
    save_table(all_rfm.describe(percentiles=[.01,.25,.5,.75,.95,.99]).T,'customer_distribution',True)
    save_table(orders[['revenue']].describe(percentiles=[.01,.25,.5,.75,.95,.99]).T,'order_distribution',True)
    cumulative=all_rfm.revenue.sort_values(ascending=False).cumsum()/all_rfm.revenue.sum()
    plt.figure();plt.plot(np.arange(1,len(cumulative)+1)/len(cumulative),cumulative);plt.xlabel('Fraction of customers, highest revenue first');plt.ylabel('Fraction of gross purchase revenue');plt.title('How concentrated is customer revenue?');figure('revenue_concentration')
    plt.figure(figsize=(10,4));sns.histplot(np.log1p(all_rfm.revenue),bins=50);plt.xlabel('log(1 + customer gross revenue GBP)');plt.title('How skewed is historical customer value?');figure('customer_value')
    plt.figure();sns.histplot(gaps,bins=50);plt.axvline(horizon,color='red',label=f'{horizon}-day threshold');plt.legend();plt.xlabel('Positive interpurchase gap, days');plt.title('What repeat-purchase gaps support the inactivity horizon?');figure('purchase_gaps')
    save_table(orders.groupby('country').agg(customers=('customer','nunique'),orders=('invoice','size'),revenue=('revenue','sum')).sort_values('revenue',ascending=False),'geography',True)
    save_table(orders.assign(month=orders.date.dt.to_period('M').astype(str)).groupby('month').agg(revenue=('revenue','sum'),customers=('customer','nunique'),orders=('invoice','size')),'monthly_health',True)
    first = orders.groupby('customer').date.min().dt.to_period('M')
    cohort = orders.copy()
    cohort['cohort'] = cohort.customer.map(first)
    cohort['month'] = cohort.date.dt.to_period('M')
    cohort['age'] = cohort.month.astype('int64')-cohort.cohort.astype('int64')
    counts = cohort.groupby(['cohort','age']).customer.nunique().unstack()
    # Unobserved cohort ages stay NaN, observed months without activity are zero.
    last_month = end.to_period('M')-1 # exclude incomplete December
    counts = counts.loc[counts.index<=last_month]
    for c in counts.index:
        max_age = last_month.ordinal-c.ordinal
        for age in counts.columns:
            counts.loc[c,age] = (0 if pd.isna(counts.loc[c,age]) else counts.loc[c,age]) if age<=max_age else np.nan
    retention = counts.div(counts[0],axis=0)
    retention.index = retention.index.astype(str)
    save_table(retention,'cohort_retention',True)
    save_table(counts.rename_axis('cohort').reset_index(),'cohort_counts')
    save_table(cohort.groupby(['cohort','age']).revenue.sum().rename('revenue').reset_index(),'cohort_revenue')
    plt.figure(figsize=(12,8));sns.heatmap(retention,cmap='Blues',vmin=0,vmax=1);plt.title('Which acquisition cohorts return in each observed month?');figure('cohort_retention')
    # Customer-level inference on untouched evaluation customers, not transaction-level pseudo-replication.
    a = test.loc[test.inactive==1,'monetary']; b = test.loc[test.inactive==0,'monetary']
    mw = stats.mannwhitneyu(a,b,alternative='two-sided')
    rng = np.random.default_rng(42)
    boot = [np.median(rng.choice(a,len(a),replace=True))-np.median(rng.choice(b,len(b),replace=True)) for _ in range(2000)]
    statistical = {'test':'Mann-Whitney U','statistic':float(mw.statistic),'p_value':float(mw.pvalue),'rank_biserial':float(2*mw.statistic/(len(a)*len(b))-1),'inactive_median':float(a.median()),'retained_median':float(b.median()),'median_difference_ci95':np.quantile(boot,[.025,.975]).tolist(),'inactive_n':len(a),'retained_n':len(b)}
    n=len(test);rate=test.inactive.mean();z=stats.norm.ppf(.975);den=1+z*z/n;center=(rate+z*z/(2*n))/den;half=z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/den
    statistical['inactive_rate_wilson_ci95']=[center-half,center+half]
    survival = survival_dataset(orders,horizon,end)
    save_table(survival,'survival_customers')
    plt.figure(figsize=(10,6))
    summaries = {}
    # Baseline cohort segments avoid using eventual total spending to explain survival.
    for label,mask in [('First observed Jan-Jun',survival.first_month<=6),('First observed Jul-Dec',survival.first_month>6)]:
        group=survival[mask];km=KaplanMeierFitter().fit(group.duration,group.event,label=label);km.plot_survival_function()
        summaries[label]={'customers':len(group),'events':int(group.event.sum()),'survival_180_days':float(km.predict(180)),'median_days':float(km.median_survival_time_)}
        curve=km.survival_function_.join(km.confidence_interval_);save_table(curve,f'survival_curve_{len(summaries)}',True)
    plt.title('Time to first inactivity spell by first-observed season');plt.xlabel('Days since first observed purchase');figure('survival')
    calibration_rows=[]
    for name,prob in [('selected',p)]:
        observed,predicted=calibration_curve(test.inactive,prob,n_bins=10,strategy='quantile')
        calibration_rows.extend([{'model':name,'predicted':x,'observed':y} for x,y in zip(predicted,observed)])
    save_table(pd.DataFrame(calibration_rows),'calibration')
    plt.figure();plt.plot(predicted,observed,'o-');plt.plot([0,1],[0,1],'--');plt.xlabel('Predicted inactivity');plt.ylabel('Observed inactivity');plt.title('Are inactivity probabilities calibrated?');figure('calibration')
    importance=permutation_importance(bundle['model'],test[FEATURES],test.inactive,scoring='neg_brier_score',n_repeats=10,random_state=42)
    save_table(pd.DataFrame({'feature':FEATURES,'mean_brier_degradation':importance.importances_mean,'std':importance.importances_std}),'global_explanations')
    # Local perturbation explanations are transparent, model-agnostic associations.
    representatives={'highest_risk':test.risk.idxmax(),'highest_priority':ranked.index[0],'borderline':(test.risk-.5).abs().idxmin()}
    local=[]
    for profile,cid in representatives.items():
        x=test.loc[[cid],FEATURES];base=float(bundle['model'].predict_proba(x)[0,1])
        for feature in FEATURES:
            changed=x.copy();changed[feature]=train[feature].median()
            local.append({'profile':profile,'customer':cid,'feature':feature,'actual':float(x[feature].iloc[0]),'training_median':float(train[feature].median()),'raw_probability_change_to_median':float(bundle['model'].predict_proba(changed)[0,1]-base)})
    save_table(pd.DataFrame(local),'local_explanations')
    monitoring=[{'measure':f'{c}_PSI','value':psi(train[c],test[c])} for c in FEATURES]
    monitoring += [{'measure':'base_rate_difference','value':float(test.inactive.mean()-train.inactive.mean())},{'measure':'test_calibration_brier','value':performance['selected_test']['brier']},{'measure':'score_PSI','value':psi(bundle['model'].predict_proba(train[FEATURES])[:,1],bundle['model'].predict_proba(test[FEATURES])[:,1])},{'measure':'value_forecast_to_actual_ratio','value':float(test.future_revenue.sum()/test.observed_future_revenue.sum())}]
    save_table(pd.DataFrame(monitoring),'monitoring')
    con=duckdb.connect(str(ROOT/'data/processed/analytics.duckdb'))
    con.register('order_frame',orders);con.execute('CREATE OR REPLACE TABLE orders AS SELECT * FROM order_frame')
    con.register('score_frame',ranked.reset_index());con.execute('CREATE OR REPLACE TABLE scores AS SELECT * FROM score_frame')
    sql_results={}
    for file in sorted((ROOT/'sql').glob('*.sql')):
        result=con.execute(file.read_text()).df();save_table(result,'sql_'+file.stem);sql_results[file.name]=len(result)
    con.close()
    result={'audit':audit,'threshold':{'discovery_end':'2010-06-01','gap_quantiles':{str(k):float(v) for k,v in quantiles.items()},'horizon_days':horizon},'windows':{name:{'cutoff':str(f.cutoff.iloc[0].date()),'prediction_end':str((f.cutoff.iloc[0]+pd.Timedelta(days=horizon)).date()),'customers':len(f),'inactive_rate':float(f.inactive.mean())} for name,f in zip(['train','validation','calibration','test'],snapshots)},'model':bundle['name'],'performance':performance,'statistics':statistical,'survival':summaries,'value':value_diagnostics,'concentration':concentration,'sql':sql_results}
    (TABLE/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (ROOT/'config/analysis.json').write_text(json.dumps({'seed':42,'horizon_days':horizon,'identity_partition':'SHA256 modulo 10: train 0-5, validation 6, calibration 7, test 8-9','margin_assumption':.3},indent=2))
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    main()
