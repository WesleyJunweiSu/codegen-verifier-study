"""Execute input-only pair comparisons in restricted Linux; no hidden dataset is mounted."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
import time
from pathlib import Path

from verifier_study.consensus import literal_calls,select_consensus
from verifier_study.test_quality import public_assertions


def invocation(call,namespace,entry_point):
    tree=ast.parse(call,mode="eval").body
    assert isinstance(tree,ast.Call)
    tree.func=ast.Subscript(value=ast.Name(id=namespace,ctx=ast.Load()),slice=ast.Constant(entry_point),ctx=ast.Load())
    return ast.unparse(ast.fix_missing_locations(tree))


def probe(code_a,entry_point,call,code_b=None):
    from evalplus.eval import untrusted_check
    # Candidate namespaces and literal inputs are rebuilt independently for each call.
    source="def __consensus_probe():\n    import random\n    import numpy as np\n"
    source+="    random.seed(20260906)\n    np.random.seed(20260906)\n    a={}\n"
    source+="    exec("+repr(code_a)+", a)\n    left="+invocation(call,"a",entry_point)+"\n"
    if code_b is None: source+="    return True\n"
    else:
        source+="    random.seed(20260906)\n    np.random.seed(20260906)\n    b={}\n"
        source+="    exec("+repr(code_b)+", b)\n    right="+invocation(call,"b",entry_point)+"\n    return bool(left == right)\n"
    status,_=untrusted_check("humaneval",source,[[]],"__consensus_probe",[True],0,[.001],fast_check=True,
                              min_time_limit=.25 if code_b is None else .5)
    return status


def write_rows(path,rows):
    path.write_text("".join(json.dumps(row)+"\n" for row in rows),encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--parent-run",default="mbpp-parser-ablation-20260905",choices=["mbpp-parser-ablation-20260905","mbpp-temperature-20260906","mbpp-development40-20260907","mbpp-confirmation-20260911"])
    args=parser.parse_args()
    if platform.system()!="Linux" or os.environ.get("VERIFIER_ISOLATED_RUN")!="1":
        raise SystemExit("Restricted Linux Docker workflow required; host execution disabled.")
    source=Path(args.input);output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    generations=[json.loads(line) for line in (source/"generations.jsonl").read_text().splitlines()]
    tests={row["task_id"]:row for row in map(json.loads,(source/"generated-tests.jsonl").read_text().splitlines())}
    visible={row["task_id"]:row for row in map(json.loads,Path("/app/mbpp-prompts.jsonl").read_text().splitlines())}
    started=time.perf_counter();inputs=[];pairs=[];validity=[];candidates=[];rejected=0
    fixtures={
        "equal":probe("def f(x): return x+1","f","f(1)","def f(x): return 1+x"),
        "unequal":probe("def f(x): return x+1","f","f(1)","def f(x): return x"),
        "both_raise":probe("def f(x): raise ValueError()","f","f(1)","def f(x): raise ValueError()"),
        "large_integer_equal":probe("def f(x): return 10**5000","f","f(1)","def f(x): return 10**5000")}
    assert fixtures=={"equal":"pass","unequal":"fail","both_raise":"fail","large_integer_equal":"pass"},fixtures
    for task_id in sorted(tests):
        pool=sorted([row for row in generations if row["task_id"]==task_id],key=lambda row:row["sample_index"])
        assert len(pool)==4
        task=visible[task_id]
        # Discard expected outputs: only literal target-call arguments are retained.
        assertions=public_assertions(task["prompt"])+[test["assertion"] for test in tests[task_id]["tests"]]
        calls,failed=literal_calls(assertions,task["entry_point"]);rejected+=failed
        inputs.extend({"task_id":task_id,**call} for call in calls)
        candidates.extend({"task_id":task_id,"sample_index":row["sample_index"],"code_sha256":hashlib.sha256(row["code"].encode()).hexdigest()} for row in pool)
        for call in calls:
            success={}
            for row in pool:
                status=probe(row["code"],task["entry_point"],call["call"])
                success[row["sample_index"]]=status=="pass"
                validity.append({"task_id":task_id,"input_index":call["input_index"],"sample_index":row["sample_index"],"status":status})
            for i,a in enumerate(pool):
                for b in pool[i+1:]:
                    status=(probe(a["code"],task["entry_point"],call["call"],b["code"])
                            if success[a["sample_index"]] and success[b["sample_index"]] else "not_comparable")
                    pairs.append({"task_id":task_id,"input_index":call["input_index"],"sample_a":a["sample_index"],
                                  "sample_b":b["sample_index"],"status":status})
        print(f"{task_id}: {len(calls)} unique literal input expressions",flush=True)
    write_rows(output/"inputs.jsonl",inputs)
    write_rows(output/"execution-success.jsonl",validity)
    write_rows(output/"pair-outcomes.jsonl",pairs)
    decisions=select_consensus(candidates,inputs,pairs)
    write_rows(output/"decisions.jsonl",decisions)
    metadata={"kind":"execution_consensus","parent_run":args.parent_run,
        "tasks":len(tests),"candidates":len(candidates),"literal_inputs":len(inputs),"rejected_nonliteral_calls":rejected,
        "candidate_input_probes":len(validity),"pair_probes":sum(row["status"]!="not_comparable" for row in pairs),
        "uncomparable_pairs":sum(row["status"]=="not_comparable" for row in pairs),"model_calls":0,"fixtures":fixtures,
        "wall_seconds":time.perf_counter()-started,"python":platform.python_version(),"evalplus":importlib.metadata.version("evalplus"),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "generations_sha256":hashlib.sha256((source/"generations.jsonl").read_bytes()).hexdigest(),
        "tests_sha256":hashlib.sha256((source/"generated-tests.jsonl").read_bytes()).hexdigest(),
        "hidden_benchmark_mounted":False,"comparison":"Python bool(left == right); exceptions never count as agreement; fixed RNG seeds before each candidate",
        "decisions_sha256":hashlib.sha256((output/"decisions.jsonl").read_bytes()).hexdigest()}
    (output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(metadata),flush=True)


if __name__=="__main__": main()
