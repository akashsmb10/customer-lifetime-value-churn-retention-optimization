import pandas as pd
from .features import snapshot

def labeled_snapshot(orders, cutoff, horizon, end):
    cutoff = pd.Timestamp(cutoff)
    if cutoff + pd.Timedelta(days=horizon) > pd.Timestamp(end):
        raise ValueError('Incomplete prediction window')
    f = snapshot(orders, cutoff)
    # Eligible customers have not already crossed the inactivity threshold.
    f = f[f.recency < horizon].copy()
    future = orders[(orders.date >= cutoff) & (orders.date < cutoff+pd.Timedelta(days=horizon))]
    f['inactive'] = (~f.index.isin(future.customer)).astype(int)
    f['cutoff'] = cutoff
    return f
