"""Record an explicit post-hoc, AI-assisted annotation; no generated-code execution."""
from __future__ import annotations
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,write_jsonl

WRONG="wrong_expected_under_public_evidence"
AMBIGUOUS="specification_ambiguity_or_conflict"
DOMAIN="outside_hidden_benchmark_contract"

# Each decision was made after reading the public task, the failing assertion, and
# diagnostic-only reference/contract source. These are not independent human labels.
annotations={
 ("Mbpp/11",1):(WRONG,"Both t characters in 'test' are first/last occurrences; removing both gives 'es', not 'est'."),
 ("Mbpp/285",4):(WRONG,"'abba' contains the substring 'abb'; trailing text does not erase the match."),
 ("Mbpp/285",6):(WRONG,"'aabb' contains 'abb' beginning at index 1."),
 ("Mbpp/285",7):(AMBIGUOUS,"The reference accepts an 'abb'/'abbb' substring inside a run of four b characters; whether the prose limits the entire run is underspecified."),
 ("Mbpp/299",4):(WRONG,"The public example aggregates second-field values per key. Keys 3,2,1 sum to 4,5,6, so the maximum is (1,6)."),
 ("Mbpp/299",5):(WRONG,"Three rows with key 1 and value 1 aggregate to (1,3), as demonstrated by repeated keys in the public example."),
 ("Mbpp/299",6):(WRONG,"Per-key totals are 3,5,7, so key 2 has the maximum total, not key 5."),
 ("Mbpp/479",4):(DOMAIN,"The hidden benchmark contract requires n>=0. The visible prose does not state that restriction; testing a negative value is out of benchmark scope, not universally invalid."),
 ("Mbpp/564",3):(WRONG,"Expected 4 is inconsistent with both plausible meanings of n: first three entries have 2 unequal pairs; all four entries have 5."),
 ("Mbpp/564",4):(AMBIGUOUS,"The prose never explains n. Expected 6 counts the whole list; the reference counts only the first n=3 entries (3 pairs)."),
 ("Mbpp/564",6):(AMBIGUOUS,"Expected 10 counts the whole list; reference counts the first n=3 entries. The visible example has n=len(list) and cannot distinguish these meanings."),
 ("Mbpp/564",7):(AMBIGUOUS,"Expected 15 counts the whole list; reference counts the first n=3 entries. The meaning of the second parameter is not specified in the prose."),
 ("Mbpp/586",4):(WRONG,"The public example defines a left rotation by n. At n=5 the last element 36 goes first; the generated expected output rotates by 4."),
 ("Mbpp/607",6):(AMBIGUOUS,"Behavior when no regex match exists is unspecified in the public prompt. Reference returns None; generated test invents a sentinel tuple."),
 ("Mbpp/607",7):(WRONG,"'match' occurs at start index 3 and exclusive end 8 in 'no match here'; (0,0) cannot identify the stated matching substring."),
 ("Mbpp/615",0):(WRONG,"For the single row, row mean is 10.5 and column means are [10,10,10,12]. [30.5] matches neither interpretation; it copies a value from a different public input."),
 ("Mbpp/615",1):(WRONG,"Single-row mean is 44, while column means reproduce the row. [34.25] matches neither; it copies the public multi-row example."),
 ("Mbpp/615",2):(WRONG,"Single-row mean is 58, while column means reproduce the row. [27.0] matches neither; it copies the public multi-row example."),
 ("Mbpp/615",3):(AMBIGUOUS,"[2.5] follows the prose's mean for each tuple; the public example and reference instead average columns."),
 ("Mbpp/615",4):(AMBIGUOUS,"[0.0] follows row-wise prose; reference returns one mean per column. Output length reflects the specification/example conflict."),
 ("Mbpp/615",5):(AMBIGUOUS,"[5.0] follows row-wise prose; public example and reference are column-wise."),
 ("Mbpp/615",6):(AMBIGUOUS,"[6.0] is the row mean; reference averages columns, conflicting with the prose."),
 ("Mbpp/615",7):(AMBIGUOUS,"[5.0] is the row mean; reference averages columns, conflicting with the prose."),
 ("Mbpp/62",6):(WRONG,"The visible list contains 3, so its minimum is 3 rather than 5."),
 ("Mbpp/7",3):(AMBIGUOUS,"The prose says words; the reference regex uses word characters including digits. Whether a digit-only token is a word is unspecified."),
 ("Mbpp/7",5):(WRONG,"'Short' has five characters, satisfying the at-least-four requirement; it must not be discarded."),
 ("Mbpp/7",6):(WRONG,"'six' has three characters and must be excluded. 'Four' and 'five' meet the threshold."),
 ("Mbpp/722",2):(WRONG,"Weight 69 is below minimum 70, so Charlie must be excluded regardless of strict/inclusive boundary semantics."),
 ("Mbpp/722",6):(WRONG,"Ivy's weight 68 is below 70; Jack meets both minima. Including Ivy violates the stated conjunction."),
 ("Mbpp/734",2):(WRONG,"The public example establishes contiguous sublists. For [1,0,1], singleton products total 2 and longer products are zero."),
 ("Mbpp/734",3):(WRONG,"Contiguous products for [-1,2] are -1,2,-2, whose sum is -1 rather than 1."),
 ("Mbpp/734",4):(WRONG,"For [2,2,2], length-1,2,3 product totals are 6,8,8, summing to 22 rather than 14."),
 ("Mbpp/734",5):(WRONG,"For [3,-1,4], length-1,2,3 totals are 6,-7,-12, summing to -13 rather than 22."),
 ("Mbpp/734",7):(WRONG,"For [1,-2,3,-4], length-1,2,3,4 totals are -2,-20,18,24, summing to 20 rather than 10."),
}

run=ROOT/"runs/mbpp-parser-ablation-20260905"
tests={row["task_id"]:row for row in read_jsonl(run/"generated-tests.jsonl")}
diagnostics=read_jsonl(run/"linux/reference-test-diagnostics.jsonl")
failed={(row["task_id"],row["test_index"]) for row in diagnostics if row["reference_status"]!="pass"}
assert set(annotations)==failed,"Audit must cover every and only reference-rejecting assertion"
rows=[]
for (task_id,index),(category,rationale) in sorted(annotations.items()):
    test=tests[task_id]["tests"][index]
    rows.append({"task_id":task_id,"test_index":index,"assertion":test["assertion"],"primary_category":category,
                 "rationale":rationale,"annotation_source":"AI-assisted source review; not independently human-validated",
                 "reference_and_contract_visible_to_annotator":True,"eligible_as_selector_input":False})
out=run/"audit";out.mkdir(exist_ok=True)
write_jsonl(out/"annotations.jsonl",rows)
write_json(out/"summary.json",{"assertions":len(rows),"tasks":len({row['task_id'] for row in rows}),
           "primary_categories":dict(collections.Counter(row["primary_category"] for row in rows)),
           "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "limitations":"Post-hoc AI-assisted, single-annotator, no agreement estimate; categories are judgments, not definitive ground truth.",
           "information_boundary":"Diagnostic-only; do not use annotations, hidden contracts or reference behavior in deployable filtering."})
print((out/"summary.json").read_text(encoding="utf-8"))
