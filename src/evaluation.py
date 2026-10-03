import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, brier_score_loss, confusion_matrix, log_loss

def metrics(y,p):
    pred = np.asarray(p)>=0.5
    return dict(roc_auc=float(roc_auc_score(y,p)),pr_auc=float(average_precision_score(y,p)),precision=float(precision_score(y,pred,zero_division=0)),recall=float(recall_score(y,pred)),f1=float(f1_score(y,pred)),brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,p)),confusion_matrix=confusion_matrix(y,pred).tolist())
