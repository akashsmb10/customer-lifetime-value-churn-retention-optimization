import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from .features import FEATURES
from .evaluation import metrics

def fit_models(train, validation, calibration, test):
    models = {'logistic':make_pipeline(FunctionTransformer(np.log1p),StandardScaler(),LogisticRegression(max_iter=2000,C=1)), 'gradient_boosting':HistGradientBoostingClassifier(max_iter=150,max_leaf_nodes=15,l2_regularization=10,random_state=42)}
    val = {}
    for name, model in models.items():
        model.fit(train[FEATURES],train.inactive)
        val[name] = metrics(validation.inactive,model.predict_proba(validation[FEATURES])[:,1])
    name = min(val,key=lambda n:val[n]['brier'])
    model = models[name]
    pcal = model.predict_proba(calibration[FEATURES])[:,1]
    calibrator = LogisticRegression(C=1e6).fit(np.log(np.clip(pcal,1e-6,1-1e-6)/(1-np.clip(pcal,1e-6,1-1e-6))).reshape(-1,1),calibration.inactive)
    raw = model.predict_proba(test[FEATURES])[:,1]
    calibrated = calibrator.predict_proba(np.log(np.clip(raw,1e-6,1-1e-6)/(1-np.clip(raw,1e-6,1-1e-6))).reshape(-1,1))[:,1]
    # Predeclared choice: use calibration only if calibration-block Brier improves.
    c = calibrator.predict_proba(np.log(np.clip(pcal,1e-6,1-1e-6)/(1-np.clip(pcal,1e-6,1-1e-6))).reshape(-1,1))[:,1]
    use = metrics(calibration.inactive,c)['brier'] < metrics(calibration.inactive,pcal)['brier']
    return dict(model=model,calibrator=calibrator,use_calibration=use,name=name,features=FEATURES), calibrated if use else raw, {'validation':val,'base_rate':metrics(test.inactive,np.repeat(train.inactive.mean(),len(test))),'raw_test':metrics(test.inactive,raw),'calibrated_test':metrics(test.inactive,calibrated),'selected_test':metrics(test.inactive,calibrated if use else raw),'calibration_used':use}
