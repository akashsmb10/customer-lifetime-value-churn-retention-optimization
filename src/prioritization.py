import numpy as np
import pandas as pd

def prioritize(frame):
    f = frame.copy()
    f['priority'] = f.risk*f.future_revenue
    f['segment'] = np.where(f.future_revenue>=f.future_revenue.median(),'High value','Low value')+' / '+np.where(f.risk>=f.risk.median(),'High risk','Low risk')
    return f.sort_values(['priority'],ascending=False)

def simulate(f, capacities=(.05,.1,.2), costs=(1,5,10), successes=(.02,.05,.1), incentives=(0,10,25), margin=.3):
    rng = np.random.default_rng(42)
    rows = []
    for cap in capacities:
        k = max(1,int(len(f)*cap))
        selections = {'risk':f.nlargest(k,'risk'),'value':f.nlargest(k,'future_revenue'),'risk_value':f.nlargest(k,'priority')}
        # Random baseline: repeated draws, using mean exposure rather than a lucky sample.
        exposures = [f.iloc[rng.choice(len(f),k,replace=False)].priority.sum() for _ in range(200)]
        for strategy in ['random',*selections]:
            exposure = float(np.mean(exposures)) if strategy=='random' else float(selections[strategy].priority.sum())
            for cost in costs:
                for success in successes:
                    for incentive in incentives:
                        gross = exposure*success
                        # incentive paid to every contacted customer, conservative scenario.
                        net = gross*margin-k*(cost+incentive)
                        rows.append((strategy,cap,k,cost,success,incentive,margin,exposure,gross,net))
    return pd.DataFrame(rows,columns=['strategy','capacity','contacts','contact_cost','assumed_success','incentive','assumed_margin','predicted_value_at_risk','scenario_retained_revenue','scenario_net_contribution'])
