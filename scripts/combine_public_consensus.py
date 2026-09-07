"""Development-adaptive composition using only public-test outcomes and saved consensus scores."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,write_jsonl,sha256


def select(public_rows,consensus_decisions):
    decisions=[]
    for consensus in consensus_decisions:
        if consensus["method"]!="execution_consensus": continue
        task_id=consensus["task_id"]
        scores={int(index):value for index,value in consensus["scores"].items()}
        counts={index:sum(row["status"]=="pass" for row in public_rows if row["task_id"]==task_id and row["sample_index"]==index)
                for index in scores}
        best=max(sorted(scores),key=lambda index:(counts[index],scores[index]["fraction"]))
        decisions.append({"task_id":task_id,"method":"public_then_consensus","sample_index":best,"accepted":True,
            "public_passes":counts,"consensus_scores":scores,"tie_break":"smallest sample_index",
            "phase":"Adaptive development composition after viewing pilot outcomes","hidden_labels_used":False})
    return decisions


def main():
    parent=ROOT/"runs/mbpp-parser-ablation-20260905"
    consensus=ROOT/"runs/mbpp-consensus-20260906"
    out=ROOT/"runs/mbpp-public-consensus-20260906";out.mkdir(parents=True,exist_ok=True)
    path=out/"decisions.jsonl"
    if path.exists(): raise SystemExit("Composition already recorded; refusing to overwrite")
    public_rows=[row for row in read_jsonl(parent/"linux/candidate-test-matrix.jsonl") if row["source"]=="public"]
    # No evaluation.jsonl, summary.json, reference data or hidden outcomes are read.
    decisions=select(public_rows,read_jsonl(consensus/"linux/decisions.jsonl"))
    write_jsonl(path,decisions)
    write_json(out/"manifest.json",{"parent_run":parent.name,"consensus_run":consensus.name,
        "adaptation":"Proposed after examining which development tasks each baseline rescues; not preregistered or confirmatory",
        "policy":"Lexicographic public passes, execution-consensus score, then smallest sample index",
        "new_model_calls":0,"new_execution_calls":0,"decisions_sha256":sha256(path),
        "source_sha256":sha256(Path(__file__)),"public_matrix_sha256":sha256(parent/"linux/candidate-test-matrix.jsonl"),
        "consensus_decisions_sha256":sha256(consensus/"linux/decisions.jsonl")})
    print("Persisted",len(decisions),"public-then-consensus decisions without reading hidden labels")


if __name__=="__main__": main()
