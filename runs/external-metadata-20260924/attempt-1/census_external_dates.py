"""Authorized, metadata-only projection of a pinned LCB snapshot.

Raw JSON framing is parsed in memory. Test payloads are never decoded, saved,
printed, or passed to an evaluator. No upstream dataset loader is imported.
"""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/external-metadata-20260924"
REVISION = "0fe84c3912ea0c4d4a78037083943e8f0c4dd505"
FILES = ["test.jsonl"] + [f"test{i}.jsonl" for i in range(2, 7)]
FIELDS = ("platform", "question_id", "contest_date", "difficulty")
START = "2025-05-20"
MAX_LINE = 16 * 1024 * 1024
MAX_TOTAL = 2 * 1024 * 1024 * 1024
MAX_SECONDS = 900


def project(record):
    """Only access the four approved keys; reject unexpected metadata types."""
    result = {}
    for key in FIELDS:
        value = record[key]
        if not isinstance(value, (str, int)) or isinstance(value, bool):
            raise ValueError("Invalid metadata type")
        result[key] = str(value)
        if len(result[key]) > 256:
            raise ValueError("Metadata too long")
    dt.datetime.fromisoformat(result["contest_date"].replace("Z", "+00:00"))
    return result


def census(rows):
    keys = [(r["platform"], r["question_id"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate task IDs: resolve snapshot semantics before enrollment")
    eligible = [r for r in rows if r["contest_date"][:10] >= START]
    return {
        "total_tasks": len(rows), "eligible_tasks": len(eligible),
        "criterion": f"contest_date >= {START}; post-identical-snapshot, not proven post-training-cutoff",
        "date_min": min((r["contest_date"] for r in rows), default=None),
        "date_max": max((r["contest_date"] for r in rows), default=None),
        "eligible_by_platform": dict(sorted(collections.Counter(r["platform"] for r in eligible).items())),
        "eligible_by_difficulty": dict(sorted(collections.Counter(r["difficulty"] for r in eligible).items())),
    }, eligible


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    auth = OUT / "authorization.json"
    if json.loads(auth.read_text(encoding="utf-8"))["scope"] != "lcb_metadata_projection_only":
        raise ValueError("Expected scoped authorization")
    if (OUT / "summary.json").exists():
        raise RuntimeError("Completed census exists; do not repeat")
    started = time.monotonic()
    total = 0
    rows = []
    sources = []
    file_name = None
    manifest = {
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dataset": "livecodebench/code_generation_lite", "revision": REVISION,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "authorization_sha256": hashlib.sha256(auth.read_bytes()).hexdigest(),
        "source_commit": subprocess.check_output(["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "retained_fields": list(FIELDS), "raw_rows_persisted": False,
        "private_test_payloads_decoded": False, "generated_code_executed": False,
        "model_calls": 0, "gpu_seconds": 0, "paid_api_calls": 0,
        "limits": {"max_total_bytes": MAX_TOTAL, "max_seconds": MAX_SECONDS, "request_timeout_seconds": 60},
        "sources": sources,
    }
    try:
        for file_name in FILES:
            url = f"https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/{REVISION}/{file_name}"
            digest = hashlib.sha256()
            count = size = 0
            req = urllib.request.Request(url, headers={"User-Agent": "codegen-verifier-study-metadata"})
            with urllib.request.urlopen(req, timeout=60) as response:
                while True:
                    if time.monotonic() - started > MAX_SECONDS:
                        raise TimeoutError("Census wall-time limit")
                    raw = response.readline(MAX_LINE + 1)
                    if not raw:
                        break
                    if len(raw) > MAX_LINE:
                        raise ValueError("Line size limit")
                    size += len(raw)
                    total += len(raw)
                    if total > MAX_TOTAL:
                        raise ValueError("Download size limit")
                    digest.update(raw)
                    # Do not retain the record or inspect any other field.
                    if raw.strip():
                        rows.append(project(json.loads(raw)))
                        count += 1
                    del raw
            sources.append({"file": file_name, "url": url, "sha256": digest.hexdigest(), "bytes": size, "rows": count})
            print(f"Projected {file_name}: {count} metadata rows", flush=True)
        summary, eligible = census(rows)
        save("task-metadata.json", rows)
        save("eligible-metadata.json", eligible)
        manifest["artifact_sha256"] = {
            name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            for name in ("task-metadata.json", "eligible-metadata.json")
        }
        save("summary.json", summary)
        manifest["status"] = "complete_metadata_only"
        print(json.dumps(summary), flush=True)
    except Exception as error:
        manifest.update(status="failed", failed_file=file_name, error_type=type(error).__name__)
        # Never serialize exception payloads, response bodies or raw task rows.
        print(f"Metadata census failed: {type(error).__name__}", flush=True)
        raise SystemExit(1) from None
    finally:
        manifest.update(downloaded_bytes=total, wall_seconds=round(time.monotonic() - started, 3))
        save("manifest.json", manifest)


if __name__ == "__main__":
    main()
