"""Controlled legacy-evaluator interventions, permitted only in isolated Linux Docker."""
from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.metadata
import json
import multiprocessing
import pickle
import platform
import queue
import sys
import os
import time
from pathlib import Path

from verifier_study import legacy_windows_eval as legacy


def diagnostic_worker(channel,solution,entry_point,inputs,expected,atol,mode):
    if mode=="unlimited_repr":
        sys.set_int_max_str_digits(0)
        return legacy._worker(channel,solution,entry_point,inputs,expected,atol)
    if mode=="original_repr":
        return legacy._worker(channel,solution,entry_point,inputs,expected,atol)
    assert mode=="omit_repr"
    namespace={"__builtins__":legacy._safe_builtins(),"__name__":"__candidate__"}
    details=[];outcomes=[]
    try:
        exec(compile(solution,"<candidate>","exec"),namespace)
        function=namespace[entry_point]
        for index,arguments in enumerate(inputs):
            try:
                output=function(*copy.deepcopy(arguments))
                # Only intervention: do not stringify function outputs for diagnostic logging.
                outcomes.append(("return","<value omitted>"))
                details.append(legacy._equivalent(output,expected[index],atol))
            except BaseException as error:
                outcomes.append(("exception",type(error).__name__))
                details.append(False)
        channel.put(("pass" if all(details) else "fail",tuple(details),tuple(outcomes),None))
    except BaseException as error:
        channel.put(("fail",tuple(details),tuple(outcomes),type(error).__name__))


def drain_first(solution,entry_point,inputs,expected,atol,mode,timeout):
    rejection=legacy.audit_code(solution)
    if rejection: return {"status":"unsafe","reason":rejection}
    context=multiprocessing.get_context("spawn")
    channel=context.Queue(maxsize=1)
    process=context.Process(target=diagnostic_worker,args=(channel,solution,entry_point,inputs,expected,atol,mode))
    process.start()
    try:
        payload=channel.get(timeout=timeout)
        process.join(1)
        status,details,outcomes,reason=payload
        return {"status":status,"reason":reason,"checked":len(details),"passed_inputs":sum(details),
                "queue_payload_bytes":len(pickle.dumps(payload)),
                "exception_types":sorted({outcome[1] for outcome in outcomes if outcome[0]=="exception"}),
                "child_alive_after_drain":process.is_alive()}
    except queue.Empty:
        return {"status":"timeout","reason":"channel_get_timeout"}
    finally:
        if process.is_alive(): process.terminate();process.join(1)
        if process.is_alive(): process.kill();process.join(1)
        channel.close();channel.join_thread()


def compare(task_id,solution,entry_point,inputs,expected,atol,timeout):
    rows=[]
    for condition in ("original","drain_first","drain_first_omit_repr","drain_first_unlimited_repr"):
        if condition=="drain_first_unlimited_repr" and task_id not in ("HumanEval/139","fixture/big_integer"): continue
        start=time.perf_counter()
        if condition=="original":
            result=legacy.check_solution(solution=solution,entry_point=entry_point,inputs=inputs,expected=expected,atol=atol,timeout_seconds=timeout)
            result={"status":result.status,"reason":result.reason,"checked":len(result.details),"passed_inputs":sum(result.details),
                    "exception_types":sorted({outcome[1] for outcome in result.outcomes if outcome[0]=="exception"})}
        else:
            mode={"drain_first":"original_repr","drain_first_omit_repr":"omit_repr","drain_first_unlimited_repr":"unlimited_repr"}[condition]
            result=drain_first(solution,entry_point,inputs,expected,atol,mode,timeout)
        row={"task_id":task_id,"condition":condition,"timeout_seconds":timeout,"inputs":len(inputs),
             "solution_sha256":hashlib.sha256(solution.encode()).hexdigest(),"wall_seconds":time.perf_counter()-start,**result}
        rows.append(row)
        print(json.dumps(row),flush=True)
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",required=True)
    parser.add_argument("--generations",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    if platform.system()!="Linux" or os.environ.get("VERIFIER_ISOLATED_RUN")!="1":
        raise SystemExit("Use the restricted Linux Docker workflow; host execution disabled.")
    os.environ["HUMANEVAL_OVERRIDE_PATH"]=args.data
    from evalplus.data import get_human_eval_plus
    from evalplus.gen.util import trusted_exec
    problems=get_human_eval_plus()
    generations={row["task_id"]:row for row in map(json.loads,Path(args.generations).read_text().splitlines())}
    ids=["HumanEval/15","HumanEval/96","HumanEval/100","HumanEval/123","HumanEval/139","HumanEval/160","HumanEval/162"]
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    path=output/"diagnostics.jsonl"
    if path.exists(): raise SystemExit("Refusing to overwrite diagnostic output")
    started=time.perf_counter();all_rows=[]
    cases=[("fixture/queue_payload","def f(): return 'x' * 1048576","f",[[]],["x"*1048576],0,2),
           ("fixture/big_integer","def f(): return 10 ** 5000","f",[[]],[10**5000],0,2)]
    for task_id in ids:
        task=problems[task_id]
        values=trusted_exec(task["prompt"]+task["canonical_solution"],task["plus_input"],task["entry_point"])
        code=generations[task_id]["code"]
        # Historical compose_solution semantics: preserve prompt prefix before its first def.
        import re
        match=re.search(r"^(?:async\s+)?def\s+",task["prompt"],re.MULTILINE)
        solution=(task["prompt"][:match.start()] if match else "")+code
        cases.append((task_id,solution,task["entry_point"],task["plus_input"],values,task["atol"],10))
    for case in cases:
        rows=compare(*case);all_rows.extend(rows)
        with path.open("a") as handle:
            for row in rows: handle.write(json.dumps(row)+"\n")
    metadata={"scope":"Controlled Linux reproduction of Windows-evaluator code; not rerun on the original Windows host",
              "task_ids":ids,"rows":len(all_rows),"model_calls":0,"wall_seconds":time.perf_counter()-started,
              "legacy_source_sha256":hashlib.sha256(Path(legacy.__file__).read_bytes()).hexdigest(),
              "diagnostic_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "data_sha256":hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
              "generations_sha256":hashlib.sha256(Path(args.generations).read_bytes()).hexdigest(),
              "python":platform.python_version(),"platform":platform.platform(),
              "default_int_max_str_digits":sys.get_int_max_str_digits(),"multiprocessing_start":"spawn",
              "packages":{distribution.metadata["Name"]:distribution.version for distribution in importlib.metadata.distributions()}}
    (output/"diagnostic-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps({key:value for key,value in metadata.items() if key!="packages"}),flush=True)


if __name__=="__main__": main()
