#!/usr/bin/env python3
"""Create the portable laboratory archive and a per-file integrity manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import stat
import zipfile

EXCLUDED = {'.venv', '.jupyter', '.local-state', '__pycache__', 'reader-output', '.DS_Store', '.pytest_cache'}
EXCLUDED_FILES = {'setup-receipt.json'}


def build(root: Path, output: Path):
    root=root.resolve(); output=output.resolve()
    paths=sorted(p for p in root.rglob('*') if p.is_file() and not any(part in EXCLUDED for part in p.relative_to(root).parts)
                 and p.name not in EXCLUDED_FILES and p.suffix not in {'.pyc','.pyo'})
    files={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.name!='file-integrity.json'}
    integrity=root/'file-integrity.json';integrity.write_text(json.dumps({'lab_version':'1.0.0','algorithm':'sha256','files':files},indent=2)+'\n')
    paths=[p for p in paths if p!=integrity]+[integrity]
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in paths:
            info=zipfile.ZipInfo.from_file(path,str(path.relative_to(root)));info.compress_type=zipfile.ZIP_DEFLATED
            # Preserve Unix launcher mode in archives; readers may need to allow local scripts.
            if path.suffix=='.command':info.external_attr=(stat.S_IFREG|0o755)<<16
            archive.writestr(info,path.read_bytes())
    return {'archive':str(output),'files':len(paths),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(build(args.root,args.output),indent=2))


if __name__=='__main__':main()
