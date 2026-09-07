"""Verify saved artifact identities, with explicit support for the initial Git CRLF transport."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def digest(raw): return hashlib.sha256(raw).hexdigest()
checks=[]
for run in sorted((ROOT/"runs").iterdir()):
    if not (run/"linux/metadata.json").exists(): continue
    metadata=json.loads((run/"linux/metadata.json").read_text())
    workflow=json.loads((run/"linux/workflow.json").read_text())
    legacy_transport=workflow["workflow_id"] in {"33947222594","33947394519","33947519157"}
    for field,name in (("generations_sha256","generations.jsonl"),("tests_sha256","generated-tests.jsonl"),
                       ("decisions_sha256","linux/decisions.jsonl")):
        if field not in metadata: continue
        artifact_root=ROOT/"runs"/metadata["parent_run"] if metadata.get("kind")=="execution_consensus" and not name.startswith("linux/") else run
        raw=(artifact_root/name).read_bytes()
        exact=digest(raw)==metadata[field]
        legacy_lf=digest(raw.replace(b"\r\n",b"\n"))==metadata[field]
        assert exact or (legacy_transport and legacy_lf),(run.name,field,"hash mismatch")
        checks.append({"run":run.name,"file":name,"match":"exact bytes" if exact else "initial Git CRLF-to-LF transport"})
    if metadata.get("kind")=="execution_consensus":
        rows=[json.loads(line) for line in (run/"linux/decisions.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(rows)==2*metadata["tasks"]
    else:
        rows=[json.loads(line) for line in (run/"linux/evaluation.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(rows)==metadata["samples"]
        assert sum(row["pass"] for row in rows)==metadata["passed"]
print(json.dumps(checks,indent=2))
