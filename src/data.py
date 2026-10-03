from pathlib import Path
import hashlib
import urllib.request
import zipfile
import pandas as pd

URL = 'https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'

def load_data(root):
    folder = Path(root) / 'data/raw'
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / 'online_retail_ii.zip'
    if not archive.exists():
        urllib.request.urlretrieve(URL, archive)
    with zipfile.ZipFile(archive) as z:
        name = next(n for n in z.namelist() if n.endswith('.xlsx'))
        target = folder / Path(name).name
        if not target.exists():
            target.write_bytes(z.read(name))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    cache = folder / 'source_lines.parquet'
    checksum = folder / 'source_lines.sha256'
    if cache.exists() and checksum.exists() and checksum.read_text()==digest:
        return pd.read_parquet(cache), digest
    sheets = pd.read_excel(target, sheet_name=None, engine='calamine')
    raw = pd.concat(sheets.values(), ignore_index=True)
    raw.columns = ['invoice', 'stock', 'description', 'quantity', 'date', 'price', 'customer', 'country']
    raw['invoice'] = raw.invoice.astype(str)
    raw['stock'] = raw.stock.astype(str)
    raw['description'] = raw.description.astype('string')
    raw.to_parquet(cache,index=False)
    checksum.write_text(digest)
    return raw, digest

def clean_data(raw):
    valid = raw.drop_duplicates().copy()
    valid = valid[valid.customer.notna() & valid.date.notna() & (valid.quantity > 0) & (valid.price > 0) & ~valid.invoice.astype(str).str.upper().str.startswith('C')].copy()
    valid['customer'] = valid.customer.astype(int).astype(str)
    valid['invoice'] = valid.invoice.astype(str)
    valid['revenue'] = valid.quantity * valid.price
    orders = valid.groupby(['customer','invoice'], as_index=False).agg(date=('date','min'), revenue=('revenue','sum'), country=('country','first'))
    return valid, orders
