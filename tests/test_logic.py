import pandas as pd
import numpy as np
import pytest
import joblib
from pathlib import Path
from src.data import clean_data
from src.features import snapshot
from src.churn import labeled_snapshot
from src.survival import survival_dataset
from src.prioritization import prioritize,simulate
from src.monitoring import psi

@pytest.fixture
def orders():
    return pd.DataFrame({'customer':['A','A','A','B'],'invoice':['1','2','3','4'],'date':pd.to_datetime(['2020-01-01','2020-01-10','2020-02-10','2020-01-20']),'revenue':[10.,20.,30.,40.],'country':['UK']*4})

def test_rfm_no_future(orders):
    f=snapshot(orders,'2020-02-01');assert f.loc['A','frequency']==2;assert f.loc['A','monetary']==30;assert f.loc['A','recency']==22

def test_prediction_boundary(orders):
    f=labeled_snapshot(orders,'2020-02-01',30,'2020-04-01');assert f.loc['A','inactive']==0;assert f.loc['B','inactive']==1

def test_incomplete_window(orders):
    with pytest.raises(ValueError):labeled_snapshot(orders,'2020-02-01',30,'2020-02-20')

def test_ineligible_already_inactive(orders):
    f=labeled_snapshot(orders,'2020-02-01',15,'2020-04-01');assert 'A' not in f.index

def test_survival_first_gap_and_censor(orders):
    s=survival_dataset(orders,30,'2020-02-15').set_index('customer');assert s.loc['A','duration']==39;assert s.loc['A','event']==1;assert s.loc['B','event']==0

def test_survival_late_revival(orders):
    s=survival_dataset(orders,30,'2020-04-01').set_index('customer');assert s.loc['A','duration']==39

def test_priority_and_budget():
    f=prioritize(pd.DataFrame({'risk':[.9,.2],'future_revenue':[10.,100.]}));assert f.index[0]==1
    s=simulate(f,capacities=(.5,),costs=(5,),successes=(0,),incentives=(10,));assert (s.scenario_net_contribution==-15).all()

def test_cleaning():
    raw=pd.DataFrame({'invoice':['1','1','C2','3','4'],'stock':['x']*5,'description':['x']*5,'quantity':[1,1,-1,1,1],'date':pd.to_datetime(['2020-01-01']*5),'price':[10,10,10,0,10],'customer':[1,1,1,1,None],'country':['UK']*5})
    lines,o=clean_data(raw);assert len(lines)==1;assert o.revenue.sum()==10

def test_psi_identity():
    assert psi(np.arange(100),np.arange(100))==0

def test_feature_stability_when_future_changes(orders):
    baseline=snapshot(orders,'2020-02-01')
    changed=orders.copy();changed.loc[changed.date>='2020-02-01','revenue']=999999
    pd.testing.assert_frame_equal(baseline,snapshot(changed,'2020-02-01'))

def test_bgnbd_daily_summary():
    from lifetimes.utils import summary_data_from_transaction_data
    data=pd.DataFrame({'customer':['A']*3,'date':pd.to_datetime(['2020-01-01','2020-01-11','2020-01-21']),'revenue':[10.,20.,30.]})
    s=summary_data_from_transaction_data(data,'customer','date',monetary_value_col='revenue',observation_period_end='2020-01-31',freq='D')
    assert s.loc['A','frequency']==2;assert s.loc['A','recency']==20;assert s.loc['A','T']==30;assert s.loc['A','monetary_value']==25

def test_clv_quadrature_against_closed_form():
    from src.clv import expected_purchases
    from lifetimes import BetaGeoFitter
    bg=BetaGeoFitter();bg.params_=pd.Series({'r':.8,'alpha':20.,'a':2.,'b':3.})
    x=np.array([0,1,5]);recency=np.array([0.,10.,20.]);age=np.array([30.,30.,30.])
    actual=expected_purchases(bg,60,x,recency,age)
    reference=bg.conditional_expected_number_of_purchases_up_to_time(60,x,recency,age)
    np.testing.assert_allclose(actual,reference,rtol=1e-8)
    np.testing.assert_allclose(expected_purchases(bg,0,x,recency,age),0)

def test_clv_low_dropout_parameters_are_finite():
    from src.clv import expected_purchases
    from lifetimes import BetaGeoFitter
    bg=BetaGeoFitter();bg.params_=pd.Series({'r':.8,'alpha':20.,'a':.01,'b':.3})
    x=np.array([0,1]);recency=np.array([0.,10.]);age=np.array([5.,30.])
    short=expected_purchases(bg,30,x,recency,age);long=expected_purchases(bg,90,x,recency,age)
    assert np.isfinite(long).all();assert (long>=short).all();assert (short>0).all()

def test_exact_prediction_window_end(orders):
    cutoff=pd.Timestamp('2020-02-10')
    f=labeled_snapshot(orders,cutoff,32,'2020-04-01');assert f.loc['A','inactive']==0
    moved=orders.copy();moved.loc[moved.invoice=='3','date']=cutoff+pd.Timedelta(days=32)
    f=labeled_snapshot(moved,cutoff,32,'2020-04-01');assert f.loc['A','inactive']==1

def test_model_load_and_value_artifact():
    root=Path(__file__).resolve().parents[1];b=joblib.load(root/'artifacts/models/churn.joblib');f=pd.read_csv(root/'artifacts/tables/customer_scores.csv');p=b['model'].predict_proba(f[b['features']]);assert np.isfinite(p).all();assert f.future_revenue.ge(0).all();assert np.isfinite(f.future_revenue).all()
