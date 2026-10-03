import numpy as np

def psi(reference,current):
    bins = np.unique(np.quantile(reference,np.linspace(0,1,11)))
    bins[0],bins[-1] = -np.inf,np.inf
    a = np.histogram(reference,bins)[0]/len(reference)
    b = np.histogram(current,bins)[0]/len(current)
    a,b = np.maximum(a,1e-6),np.maximum(b,1e-6)
    return float(np.sum((b-a)*np.log(b/a)))
