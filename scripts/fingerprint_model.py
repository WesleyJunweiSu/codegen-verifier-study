"""Hash the reused checkpoint and tokenizer as data; never copy model weights to Git."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("model_path")
parser.add_argument("--output",default="configs/model-fingerprint.json")
args=parser.parse_args()
root=Path(args.model_path)
rows=[]
for path in sorted(root.iterdir()):
    if path.is_file() and (path.suffix in (".json",".safetensors",".jinja") or path.name=="merges.txt"):
        digest=hashlib.sha256()
        with path.open("rb") as handle:
            while block:=handle.read(8*1024*1024): digest.update(block)
        rows.append({"file":path.name,"bytes":path.stat().st_size,"sha256":digest.hexdigest()})
Path(args.output).write_text(json.dumps({"model_id":"Qwen/Qwen3-4B","recorded_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "timing":"Recorded after first pilot; local checkpoint reused unchanged from prior study","files":rows},indent=2)+"\n")
print("Fingerprint saved for",len(rows),"files")
