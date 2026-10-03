import pandas as pd

def survival_dataset(orders, threshold, end):
    """Time from first observed purchase to FIRST threshold-length gap; revival allowed afterward."""
    end = pd.Timestamp(end)
    rows = []
    for customer, group in orders.groupby('customer'):
        dates = sorted(pd.to_datetime(group.date).unique())
        first = pd.Timestamp(dates[0])
        event_date = None
        for i, date in enumerate(dates):
            date = pd.Timestamp(date)
            following = pd.Timestamp(dates[i+1]) if i+1 < len(dates) else end
            candidate = date + pd.Timedelta(days=threshold)
            if candidate <= following and candidate <= end:
                event_date = candidate
                break
        rows.append((customer, ((event_date or end)-first).total_seconds()/86400, int(event_date is not None), first.month))
    return pd.DataFrame(rows, columns=['customer','duration','event','first_month'])
