"""Official EvalPlus checking primitives, run only inside the isolated Linux container."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import time
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset",choices=["humaneval","mbpp"],required=True)
    parser.add_argument("--data",required=True)
    parser.add_argument("--generations",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    if platform.system()!="Linux" or os.environ.get("VERIFIER_ISOLATED_RUN")!="1":
        raise SystemExit("Use the restricted Linux Docker workflow; host execution is disabled.")
    os.environ["HUMANEVAL_OVERRIDE_PATH"]=args.data
    os.environ["MBPP_OVERRIDE_PATH"]=args.data
    from evalplus.data import get_human_eval_plus,get_mbpp_plus
    from evalplus.eval import untrusted_check
    from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
    from evalplus.gen.util import trusted_exec
    problems=get_human_eval_plus() if args.dataset=="humaneval" else get_mbpp_plus()
    generations=[json.loads(line) for line in Path(args.generations).read_text().splitlines() if line]
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    rows=[];oracle_cache={};started=time.perf_counter()
    # Known correct/wrong/exception fixtures check the checking contract, not task performance.
    fixtures=[("correct","def f(x): return x+1","pass"),("wrong","def f(x): return x","fail"),
              ("exception","def f(x): raise ValueError()","fail")]
    fixture_results={}
    for name,code,expected_status in fixtures:
        status,_=untrusted_check("humaneval",code,[[1]],"f",[2],0,[0.001],fast_check=True)
        assert status==expected_status,(name,status)
        fixture_results[name]=status
    for row in generations:
        task=problems[row["task_id"]]
        if row["task_id"] not in oracle_cache:
            oracle={}
            for mode in ("base","plus"):
                values,times=trusted_exec(task["prompt"]+task["canonical_solution"],task[mode+"_input"],task["entry_point"],
                                         record_time=True,output_not_none=args.dataset=="mbpp" and task["entry_point"] in MBPP_OUTPUT_NOT_NONE_TASKS)
                oracle[mode]=(values,times)
            oracle_cache[row["task_id"]]=oracle
        code=row["code"]
        # Match the historical generation adapter: restore only pre-definition imports/docstrings.
        match=re.search(r"^(?:async\s+)?def\s+",task["prompt"],re.MULTILINE)
        if re.search(r"^\s*(?:async\s+)?def\s+",code,re.MULTILINE):
            solution=(task["prompt"][:match.start()] if match else "")+code
        else:
            solution=task["prompt"]+code
        evaluated={"task_id":row["task_id"],"sample_index":row["sample_index"],"code_sha256":hashlib.sha256(code.encode()).hexdigest()}
        for mode in ("base","plus"):
            expected,reference_times=oracle_cache[row["task_id"]][mode]
            status,details=untrusted_check(args.dataset,solution,task[mode+"_input"],task["entry_point"],expected,task["atol"],reference_times,fast_check=True)
            evaluated[mode+"_status"]=status
            evaluated[mode+"_checked"]=len(details)
        evaluated["pass"]=evaluated["base_status"]==evaluated["plus_status"]=="pass"
        rows.append(evaluated)
        with (output/"evaluation.jsonl").open("a") as handle: handle.write(json.dumps(evaluated)+"\n")
        print(json.dumps(evaluated),flush=True)
    metadata={"dataset":args.dataset,"dataset_sha256":hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
              "generations_sha256":hashlib.sha256(Path(args.generations).read_bytes()).hexdigest(),
              "evalplus":importlib.metadata.version("evalplus"),"python":platform.python_version(),"platform":platform.platform(),
              "implementation":"Official evalplus.eval.untrusted_check and evalplus.gen.util.trusted_exec; custom serial orchestration, not upstream CLI",
              "fixtures":fixture_results,"samples":len(rows),"passed":sum(row["pass"] for row in rows),
              "wall_seconds":time.perf_counter()-started}
    (output/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata),flush=True)


if __name__=="__main__":
    main()
