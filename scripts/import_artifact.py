"""Import an evaluation ZIP without permitting paths outside the chosen run directory."""
import argparse
import json
import zipfile
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("archive")
parser.add_argument("output")
parser.add_argument("--workflow-id",required=True)
parser.add_argument("--commit",required=True)
args=parser.parse_args()
target=Path(args.output).resolve()
target.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(args.archive) as archive:
    for item in archive.infolist():
        destination=(target/item.filename).resolve()
        if not destination.is_relative_to(target): raise ValueError("Unsafe archive path")
        if item.is_dir(): destination.mkdir(parents=True,exist_ok=True)
        else:
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(archive.read(item))
(target/"workflow.json").write_text(json.dumps({"workflow_id":args.workflow_id,"source_commit":args.commit,
    "url":f"https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/{args.workflow_id}"},indent=2)+"\n")
print("Imported",target)
