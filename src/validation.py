import numpy as np

def validate_snapshot(f,cutoff):
    assert (f['last']<cutoff).all()
    assert (f['first']<=f['last']).all()
    assert (f.frequency>=1).all()
    assert (f.recency>=0).all()
    assert np.isfinite(f.select_dtypes('number')).all().all()
