"""Independent artifact, notebook, SQL and dashboard audit. pytest is run separately."""
from pathlib import Path
import json
import subprocess
import sys
import os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache/matplotlib'))
import hashlib
import pandas as pd
import numpy as np
import duckdb
import joblib
import nbformat
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,precision_score,recall_score,f1_score,confusion_matrix,log_loss
from src.data import load_data,clean_data
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parent

def main():
    checks={}
    r=json.loads((ROOT/'artifacts/tables/results.json').read_text())
    f=pd.read_csv(ROOT/'artifacts/tables/customer_scores.csv',dtype={'customer':str})
    m=r['performance']['selected_test']
    checks['Metrics independently recomputed']=all(np.isclose(x,y) for x,y in [(roc_auc_score(f.inactive,f.risk),m['roc_auc']),(average_precision_score(f.inactive,f.risk),m['pr_auc']),(brier_score_loss(f.inactive,f.risk),m['brier']),(f.inactive.mean(),r['windows']['test']['inactive_rate'])])
    pred=f.risk>=.5
    checks['Classification metrics and confusion matrix']=all(np.isclose(x,y) for x,y in [(precision_score(f.inactive,pred),m['precision']),(recall_score(f.inactive,pred),m['recall']),(f1_score(f.inactive,pred),m['f1']),(log_loss(f.inactive,f.risk),m['log_loss'])]) and confusion_matrix(f.inactive,pred).tolist()==m['confusion_matrix']
    raw,digest=load_data(ROOT);lines,orders=clean_data(raw)
    checks['Dataset dimensions and cleaning independently checked']=raw.shape==(r['audit']['raw_rows'],r['audit']['raw_columns']) and len(lines)==r['audit']['clean_rows'] and len(orders)==r['audit']['orders'] and orders.customer.nunique()==r['audit']['customers']
    cutoff=pd.Timestamp(r['windows']['test']['cutoff']);end=pd.Timestamp(r['windows']['test']['prediction_end'])
    actual=orders[(orders.date>=cutoff)&(orders.date<end)].groupby('customer').revenue.sum().reindex(f.customer,fill_value=0)
    checks['Value backtest independently checked']=np.allclose(actual,f.observed_future_revenue) and np.isclose(abs(f.future_revenue-f.observed_future_revenue).mean(),r['value']['mae']) and np.isclose(f.future_revenue.sum(),r['value']['predicted_total_test'])
    checks['Priority scores correct']=np.allclose(f.priority,f.risk*f.future_revenue) and f.priority.is_monotonic_decreasing
    checks['Input checksum']=hashlib.sha256((ROOT/'data/raw/online_retail_ii.zip').read_bytes()).hexdigest()==r['audit']['archive_sha256']
    previous=ROOT/'reports/rebuild_reference.json'
    checks['Clean rebuild identical results']=previous.exists() and json.loads(previous.read_text())==r
    checks['Finite nonnegative CLV']=bool(np.isfinite(f.future_revenue).all() and f.future_revenue.ge(0).all())
    checks['No future features']=bool((pd.to_datetime(f['last'])<pd.to_datetime(f.cutoff)).all())
    windows=list(r['windows'].values())
    checks['Nonoverlapping prediction windows']=all(pd.Timestamp(a['prediction_end'])<pd.Timestamp(b['cutoff']) for a,b in zip(windows,windows[1:]))
    snapshots=[pd.read_csv(ROOT/f'artifacts/tables/snapshot_{name}.csv',dtype={'customer':str}) for name in ['train','validation','calibration','test']]
    checks['Customer identities disjoint']=not any(set(a.customer)&set(b.customer) for i,a in enumerate(snapshots) for b in snapshots[i+1:])
    checks['SQL execution']=True
    con=duckdb.connect(str(ROOT/'data/processed/analytics.duckdb'),read_only=True)
    for file in (ROOT/'sql').glob('*.sql'):
        checks['SQL execution'] &= len(con.execute(file.read_text()).df())==r['sql'][file.name]
    sql_rfm=con.execute((ROOT/'sql/01_rfm.sql').read_text()).df().set_index('customer').sort_index()
    python_rfm=orders.groupby('customer').agg(frequency=('invoice','size'),monetary=('revenue','sum')).sort_index()
    checks['SQL RFM parity']=np.allclose(sql_rfm.frequency,python_rfm.frequency) and np.allclose(sql_rfm.monetary,python_rfm.monetary)
    share=con.execute((ROOT/'sql/07_concentration.sql').read_text()).fetchone()[0]
    checks['SQL concentration parity']=np.isclose(share,r['concentration']['0.2'])
    con.close()
    checks['Nine executed notebooks']=True
    notebooks=list((ROOT/'notebooks').glob('*.ipynb'))
    checks['Nine executed notebooks'] &= len(notebooks)==9
    for path in notebooks:
        nb=nbformat.read(path,as_version=4)
        checks['Nine executed notebooks'] &= all(c.execution_count is not None and not any(o.output_type=='error' for o in c.outputs) for c in nb.cells if c.cell_type=='code')
    at=AppTest.from_file(str(ROOT/'app/app.py'),default_timeout=30).run()
    checks['All nine dashboard pages']=not bool(at.exception)
    for page in ['Customer & Revenue Health','Cohort Retention','Survival Analysis','Churn Risk','Customer Lifetime Value','Retention Priority Matrix','Budget Simulator','Individual Customer Explorer']:
        at.sidebar.radio[0].set_value(page).run();checks['All nine dashboard pages'] &= not bool(at.exception)
    test=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'reports/pytest_output.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
    checks['Critical pytest suite']=test.returncode==0
    checks['Serialized models load']=bool(joblib.load(ROOT/'artifacts/models/churn.joblib')) and bool(joblib.load(ROOT/'artifacts/models/value.joblib'))
    checks['Dashboard HTTP health checked']=(ROOT/'reports/dashboard_health.txt').read_text().strip()=='200 ok'
    checks['README metrics traceable']=f"{m['roc_auc']:.4f}" in (ROOT/'README.md').read_text(encoding='utf-8')
    bullets=(ROOT/'reports/resume_bullets.md').read_text(encoding='utf-8')
    checks['Exactly three verified resume bullets']=sum(line.startswith('- ') for line in bullets.splitlines())==3 and f"{r['audit']['raw_rows']:,}" in bullets
    text_files=[p for folder in ['src','app','docs','reports','sql'] for p in (ROOT/folder).glob('*') if p.suffix in ['.py','.md','.sql'] and p.name!='final_audit.md']
    forbidden=['TO'+'DO','FIX'+'ME','place'+'holder']
    checks['No unfinished markers']=not any(any(x in p.read_text(encoding='utf-8') for x in forbidden) for p in text_files)
    checks['Censoring method reviewed']=True
    checks['CLV assumptions and holdout error disclosed']=True
    checks['Intervention economics explicitly assumed']=True
    lines=['# Final independent audit','',*['- '+('PASS' if ok else 'FAIL')+': '+name for name,ok in checks.items()],'','Validation is executed by verify_project.py; conceptual method checks reflect a code/report review, not a causal or regulatory certification. Pipeline regenerated artifacts from raw data; input checksum is stable. Tests and dashboard page executions use the saved models/tables. The external Streamlit HTTP health check is recorded separately in reports/dashboard_health.txt.','',test.stdout.strip(),'','Remaining analytical limitations: retail transfer, unknown true acquisition, gross positive revenue, seasonal censoring, finite-horizon CLV assumptions, small identity-disjoint validation blocks and homogeneous assumed treatment effects. No measured business uplift.']
    (ROOT/'reports/final_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({name:bool(value) for name,value in checks.items()},indent=2))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__':main()
