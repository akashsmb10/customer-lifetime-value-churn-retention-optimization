"""Install a task-local official Node LTS binary; no system settings change."""
from pathlib import Path
import json
import hashlib
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def main():
    folder=ROOT/'.tools';folder.mkdir(exist_ok=True)
    releases=json.load(urllib.request.urlopen('https://nodejs.org/dist/index.json',timeout=30))
    version=next(r['version'] for r in releases if r.get('lts') and 'win-x64-zip' in r.get('files',[]))
    name=f'node-{version}-win-x64.zip';base=f'https://nodejs.org/dist/{version}/'
    archive=folder/name
    if not archive.exists():urllib.request.urlretrieve(base+name,archive)
    checksums=urllib.request.urlopen(base+'SHASUMS256.txt',timeout=30).read().decode()
    expected=next(line.split()[0] for line in checksums.splitlines() if line.split()[-1]==name)
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise ValueError('Node archive checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        for entry in z.namelist():
            target=(folder/entry).resolve()
            if folder.resolve() not in target.parents:raise ValueError('Archive entry outside tools folder')
        z.extractall(folder)
    print(folder/f'node-{version}-win-x64/node.exe')

if __name__=='__main__':main()
