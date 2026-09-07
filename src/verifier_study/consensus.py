"""Extract public literal inputs and choose candidates from label-blind pair outcomes."""
import ast
import hashlib


def literal_calls(assertions,entry_point):
    calls=[];seen=set();rejected=0
    for statement in assertions:
        try: tree=ast.parse(statement)
        except SyntaxError: rejected+=1;continue
        for node in ast.walk(tree):
            if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!=entry_point: continue
            try:
                for arg in node.args: ast.literal_eval(arg)
                for kw in node.keywords:
                    if kw.arg is None: raise ValueError("dictionary expansion")
                    ast.literal_eval(kw.value)
            except (ValueError,TypeError,SyntaxError): rejected+=1;continue
            key=ast.dump(node,include_attributes=False)
            if key in seen: continue
            seen.add(key)
            calls.append({"input_index":len(calls),"call":ast.unparse(node),"ast_sha256":hashlib.sha256(key.encode()).hexdigest()})
    return calls,rejected


def select_consensus(candidates,inputs,pairs):
    decisions=[]
    for task_id in sorted({row["task_id"] for row in candidates}):
        pool=sorted([row for row in candidates if row["task_id"]==task_id],key=lambda row:row["sample_index"])
        evidence=[row for row in pairs if row["task_id"]==task_id]
        lookup={(row["input_index"],row["sample_a"],row["sample_b"]):row for row in evidence}
        task_inputs=[row for row in inputs if row["task_id"]==task_id]
        representatives={}
        for row in pool: representatives.setdefault(row["code_sha256"],row)
        for method in ("execution_consensus","unique_code_consensus"):
            scores={}
            for candidate in pool:
                others=[row for row in (pool if method=="execution_consensus" else list(representatives.values()))
                        if (row["sample_index"]!=candidate["sample_index"] if method=="execution_consensus"
                            else row["code_sha256"]!=candidate["code_sha256"])]
                agreements=0
                for inp in task_inputs:
                    for other in others:
                        a,b=sorted((candidate["sample_index"],other["sample_index"]))
                        agreements+=lookup[(inp["input_index"],a,b)]["status"]=="pass"
                comparisons=len(others)*len(task_inputs)
                scores[candidate["sample_index"]]={"agreements":agreements,"comparisons":comparisons,
                    "fraction":agreements/comparisons if comparisons else 0.0}
            best=max(pool,key=lambda row:scores[row["sample_index"]]["fraction"])
            decisions.append({"task_id":task_id,"method":method,"sample_index":best["sample_index"],"accepted":True,
                "scores":scores,"inputs":len(task_inputs),"tie_break":"smallest sample_index",
                "fallback":"first candidate when no comparisons or all scores tie","hidden_labels_used":False})
    return decisions
