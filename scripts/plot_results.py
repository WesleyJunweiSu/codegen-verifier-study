"""Generate standalone scientific figures from recorded results; no model execution."""
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/".analysis-packages"))
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/"cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pilot=json.loads((ROOT/"runs/mbpp-pilot-20260905/summary.json").read_text())
fig,axes=plt.subplots(1,2,figsize=(10,4.3),layout="constrained")
methods=["first","public_tests","raw_tests","filtered_tests"]
names=["First candidate","Public examples","Generated tests","Filtered tests"]
counts=[pilot["methods"][method]["correct_returned"] for method in methods]
axes[0].barh(names,counts,color=["#64748b","#0e7490","#a16207","#a16207"])
for i,count in enumerate(counts): axes[0].text(count-.22,i,f"{count}/20",va="center",ha="right",fontsize=10,color="white")
axes[0].axvline(pilot["oracle_tasks"],color="#334155",linestyle="--",label="Candidate oracle: 12/20")
axes[0].set_xlim(0,20);axes[0].set_xlabel("Correct returned programs (all 20 tasks)")
axes[0].set_title("A. Selection did not close the oracle gap",loc="left",fontsize=11)
axes[0].legend(loc="lower right",fontsize=8);axes[0].invert_yaxis()
rejected=pilot["reference_rejected_assertions"]
passed=pilot["generated_assertions"]-rejected
axes[1].barh(["Generated\nassertions"],[passed],height=.22,color="#0e7490",label=f"Reference passes: {passed}")
axes[1].barh(["Generated\nassertions"],[rejected],left=[passed],height=.22,color="#b45309",label=f"Reference rejects: {rejected}")
axes[1].set_xlim(0,160);axes[1].set_xlabel("Parsed assertions (120 across 15 tasks)")
axes[1].set_title("B. Test quality remains a bottleneck",loc="left",fontsize=11)
axes[1].legend(loc="lower left",fontsize=9)
axes[1].text(5,.3,"5/20 tasks produced no accepted assertion syntax.\nReference rejection is diagnostic, not a universal\nproof of an incorrect expected value.",fontsize=9,va="bottom")
axes[1].set_ylim(-.55,.75)
for axis in axes:
    axis.spines[["top","right"]].set_visible(False)
    axis.grid(axis="x",alpha=.15);axis.set_axisbelow(True)
fig.suptitle("Qwen3-4B / MBPP+ development pilot — 20 tasks, 4 candidates each",fontsize=12)
target=ROOT/"reports/figures";target.mkdir(parents=True,exist_ok=True)
for extension in ("png","pdf","svg"): fig.savefig(target/f"pilot-results.{extension}",dpi=180)
# Matplotlib includes redundant spaces at SVG path-line endings; keep generated diffs clean.
svg=target/"pilot-results.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8",newline="\n")
print("Saved report figures")
