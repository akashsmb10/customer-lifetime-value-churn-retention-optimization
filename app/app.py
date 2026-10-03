from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
TABLE=ROOT/'artifacts/tables'
st.set_page_config(page_title='Retention Decision Studio',page_icon='📊',layout='wide')
st.title('Customer Value & Retention Decision Studio')
st.caption('Public retail case study • monetary amounts in GBP • historical evaluation, not a live banking system')
@st.cache_data
def load():
    return json.loads((TABLE/'results.json').read_text()),pd.read_csv(TABLE/'customer_scores.csv',dtype={'customer':str})
r,customers=load()
pages=['Executive Overview','Customer & Revenue Health','Cohort Retention','Survival Analysis','Churn Risk','Customer Lifetime Value','Retention Priority Matrix','Budget Simulator','Individual Customer Explorer']
page=st.sidebar.radio('Explore',pages)
st.sidebar.info('Observed = historical data. Estimated = model output. Scenario = assumptions. No causal uplift is measured.')
def table(name):
    st.dataframe(pd.read_csv(TABLE/f'{name}.csv'),width='stretch')
def image(name):
    st.image(str(ROOT/f'artifacts/figures/{name}.png'))
if page=='Executive Overview':
    a,b,c=st.columns(3)
    a.metric('Observed customers',f"{r['audit']['customers']:,}")
    b.metric('Holdout inactivity',f"{r['windows']['test']['inactive_rate']:.1%}")
    c.metric('Holdout ROC-AUC',f"{r['performance']['selected_test']['roc_auc']:.3f}")
    st.write(f"Prioritize limited contact capacity using estimated inactivity and {r['threshold']['horizon_days']}-day future gross revenue. Approve deployment only after a randomized retention pilot.")
    table('segments')
elif page=='Customer & Revenue Health':
    m=pd.read_csv(TABLE/'monthly_health.csv').set_index('month');st.line_chart(m[['revenue']]);table('geography')
    image('revenue_concentration');image('customer_value');table('customer_distribution')
    st.write('Gross positive purchase revenue excludes returns and is not net revenue or profit.')
elif page=='Cohort Retention':
    image('cohort_retention');table('cohort_retention')
    st.write('First observed purchase is not proven acquisition. Blank cells are unobserved ages; later revival counts as monthly activity.')
elif page=='Survival Analysis':
    image('survival');st.json(r['survival'])
    st.write('Event: first completed inactivity spell. Customers without a completed spell are right censored. Seasonal comparisons are descriptive.')
elif page=='Churn Risk':
    st.json(r['performance']);image('calibration');table('global_explanations')
elif page=='Customer Lifetime Value':
    st.json(r['value']);st.scatter_chart(customers,x='future_revenue',y='observed_future_revenue')
    st.warning('Finite-horizon gross revenue estimates, not lifetime accounting profit. Monetary independence and seasonality are limitations.')
elif page=='Retention Priority Matrix':
    st.scatter_chart(customers,x='risk',y='future_revenue',color='segment');table('segments')
    st.write('High value/high risk: test targeted outreach. High value/low risk: service quality. Low value/high risk: low-cost channels. Low value/low risk: routine nurture.')
elif page=='Budget Simulator':
    capacity=st.slider('Contact capacity (%)',1,30,10)/100
    success=st.slider('Assumed fraction of risk prevented',0.0,.3,.05,.01)
    cost=st.number_input('Contact cost GBP',0.0,100.0,5.0)
    incentive=st.number_input('Incentive paid per contacted customer GBP',0.0,100.0,10.0)
    margin=st.slider('Assumed contribution margin',0.0,1.0,.3,.05)
    k=max(1,int(len(customers)*capacity));rows=[]
    for name,column in [('Churn risk','risk'),('Value','future_revenue'),('Risk × value','priority')]:
        f=customers.nlargest(k,column);gross=f.priority.sum()*success
        rows.append({'strategy':name,'contacts':k,'scenario_retained_revenue':gross,'scenario_net_contribution':gross*margin-k*(cost+incentive)})
    gross=customers.priority.mean()*k*success
    rows.append({'strategy':'Random expected baseline','contacts':k,'scenario_retained_revenue':gross,'scenario_net_contribution':gross*margin-k*(cost+incentive)})
    st.dataframe(pd.DataFrame(rows),width='stretch');st.warning('Scenario arithmetic assumes homogeneous effectiveness and that preventing inactivity preserves the forecast revenue. This is not an uplift estimate or observed ROI.')
elif page=='Individual Customer Explorer':
    cid=st.selectbox('Customer',customers.customer.tolist());st.dataframe(customers[customers.customer==cid].T.astype(str))
    table('local_explanations');st.write('Local median-replacement explanations describe model sensitivity, not causes or recommended feature manipulation.')
