"""Export verified artifacts for the public, client-side dashboard."""
from pathlib import Path
import json
import math
import shutil
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web'

def records(name):
    frame=pd.read_csv(ROOT/f'artifacts/tables/{name}.csv',dtype={'customer':str} if name in ['customer_scores','local_explanations'] else None)
    return json.loads(frame.to_json(orient='records'))

def build():
    data={'results':json.loads((ROOT/'artifacts/tables/results.json').read_text())}
    for name in ['customer_scores','segments','monthly_health','geography','global_explanations','local_explanations','monitoring','cohort_retention','churn_sensitivity','survival_curve_1','survival_curve_2']:
        data[name]=records(name)
    (WEB/'data.js').write_text('window.RETENTION_DATA='+json.dumps(data,allow_nan=False,separators=(',',':'))+';\n',encoding='utf-8')
    images=WEB/'figures';images.mkdir(exist_ok=True)
    for name in ['calibration','cohort_retention','customer_value','purchase_gaps','revenue_concentration','survival']:
        shutil.copy2(ROOT/f'artifacts/figures/{name}.png',images/f'{name}.png')
    print(f'Exported {len(data["customer_scores"])} scored customers and verified chart/table artifacts.')

if __name__=='__main__':build()
