import numpy as np
import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
from scipy.stats import spearmanr
from scipy.special import roots_jacobi

def expected_purchases(bg, horizon, frequency, recency, age, nodes=96):
    """Integrate finite-horizon BG/NBD expectation; stable even when fitted a < 1.

    Given alive, lambda|history ~ Gamma(r+x, alpha+T), p|history ~ Beta(a,b+x).
    E[N(h)|lambda,p,alive] = (1-exp(-lambda*p*h))/p.
    Jacobi quadrature integrates the Beta density without requiring a>1.
    """
    x=np.asarray(frequency,dtype=int);age=np.asarray(age,dtype=float)
    r,alpha,a,b=[float(bg.params_[key]) for key in ['r','alpha','a','b']]
    output=np.empty(len(x))
    for count in np.unique(x):
        mask=x==count
        z,weights=roots_jacobi(nodes,b+count-1,a-1)
        probability=(z+1)/2
        weights=weights/weights.sum()
        conditional=-np.expm1(-(r+count)*np.log1p(horizon*probability[None,:]/(alpha+age[mask,None])))/probability[None,:]
        output[mask]=conditional@weights
    alive=np.asarray(bg.conditional_probability_alive(x,recency,age))
    return output*alive

def estimate_value(orders, cutoff, horizon):
    hist = orders[orders.date < pd.Timestamp(cutoff)].copy()
    # Monetary model uses positive daily transaction revenue; frequency excludes first purchase day.
    daily = hist.assign(date=hist.date.dt.normalize()).groupby(['customer','date'],as_index=False).revenue.sum()
    s = summary_data_from_transaction_data(daily,'customer','date',monetary_value_col='revenue',observation_period_end=pd.Timestamp(cutoff)-pd.Timedelta(days=1),freq='D')
    bg = BetaGeoFitter(penalizer_coef=0.01).fit(s.frequency,s.recency,s['T'])
    repeat = s[(s.frequency>0)&(s.monetary_value>0)]
    correlation = spearmanr(repeat.frequency,repeat.monetary_value)
    gg = GammaGammaFitter(penalizer_coef=0.0).fit(repeat.frequency,repeat.monetary_value,q_constraint=True)
    if gg.params_['q'] <= 1.000001:
        raise ValueError('Gamma-Gamma population mean is undefined at q <= 1')
    s['expected_purchases'] = expected_purchases(bg,horizon,s.frequency,s.recency,s['T'])
    s['expected_order_value'] = gg.conditional_expected_average_profit(s.frequency,s.monetary_value)
    s['future_revenue'] = s.expected_purchases*s.expected_order_value
    s['simple_revenue'] = (s.frequency+1)/(s['T']+1)*horizon*hist.groupby('customer').revenue.mean().reindex(s.index)
    if not np.isfinite(s.future_revenue).all() or (s.future_revenue<0).any():
        raise ValueError('Invalid value forecasts')
    return s, bg, gg, {'spearman_r':float(correlation.statistic),'p_value':float(correlation.pvalue),'repeat_customers':len(repeat),'bg_parameters':bg.params_.to_dict(),'gg_parameters':gg.params_.to_dict()}
