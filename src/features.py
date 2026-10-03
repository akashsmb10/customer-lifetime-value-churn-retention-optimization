import pandas as pd

FEATURES = ['recency', 'frequency', 'monetary', 'aov', 'tenure', 'recent_orders']

def snapshot(orders, cutoff):
    cutoff = pd.Timestamp(cutoff)
    history = orders[orders.date < cutoff]
    f = history.groupby('customer').agg(first=('date','min'), last=('date','max'), frequency=('invoice','nunique'), monetary=('revenue','sum'))
    f['recency'] = (cutoff - f['last']).dt.total_seconds()/86400
    f['tenure'] = (cutoff - f['first']).dt.total_seconds()/86400
    f['aov'] = f.monetary/f.frequency
    f['recent_orders'] = history[history.date >= cutoff-pd.Timedelta(days=90)].groupby('customer').size().reindex(f.index,fill_value=0)
    return f
