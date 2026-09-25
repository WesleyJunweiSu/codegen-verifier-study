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
# Pinned HF tree API size/LFS SHA256 metadata, checked 2026-09-24.
EXPECTED = dict(zip(FILES, [
    (1252609773, "2bd02b38beb48e8c46b5b9987095d999ff38cd8efc255ea5d58974317c48f63f"),
    (713377060, "095df7c5daf15f882c51a9deb84085cff1e073495a5dbcf95015a564d485f3a3"),
    (623360766, "28ed26cc83363ce3f1fe2d5fad9f8393077beb1907b167a31bd3b32f80801b79"),
    (1204644685, "d711138ddaebfcf5f8ec6a4283ee677298c0f5c5d374a235af92aaf0584510da"),
    (557699297, "7f77571c2a6df0c2a72a3277650309f67e01e0008e18117e624633df53f81214"),
    (134303240, "bb4c364f71921c4495a6ad15abe1a927350b720009f4933e2e71f8af0f6fd1f5"),
]))
FIELDS = ("platform", "question_id", "contest_date", "difficulty")
START = "2025-05-20"
MAX_LINE = 128 * 1024 * 1024
MAX_TOTAL = sum(size for size, digest in EXPECTED.values())
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
    phase = "initialization"
    manifest = {
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "dataset": "livecodebench/code_generation_lite", "revision": REVISION,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "authorization_sha256": hashlib.sha256(auth.read_bytes()).hexdigest(),
        "source_commit": subprocess.check_output(["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "retained_fields": list(FIELDS), "raw_rows_persisted": False,
        "private_test_payloads_decoded": False, "generated_code_executed": False,
        "model_calls": 0, "gpu_seconds": 0, "paid_api_calls": 0,
        "limits": {"max_total_bytes": MAX_TOTAL, "max_line_bytes": MAX_LINE, "max_seconds": MAX_SECONDS, "request_timeout_seconds": 60},
        "sources": sources,
    }
    try:
        for file_name in FILES:
            cache_name = file_name + ".metadata.json"
            cache_path = OUT / cache_name
            if cache_path.exists():
                phase = "verify_metadata_cache"
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if cached["revision"] != REVISION or (cached["source"]["bytes"], cached["source"]["sha256"]) != EXPECTED[file_name]:
                    raise ValueError("Cache source mismatch")
                if not all(set(row) == set(FIELDS) and project(row) == row for row in cached["rows"]):
                    raise ValueError("Cache projection mismatch")
                canonical = json.dumps(cached["rows"], sort_keys=True).encode()
                if hashlib.sha256(canonical).hexdigest() != cached["projection_sha256"]:
                    raise ValueError("Cache digest mismatch")
                rows.extend(cached["rows"])
                sources.append(cached["source"])
                print(f"Reused {file_name}: {len(cached['rows'])} metadata rows", flush=True)
                continue
            url = f"https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/{REVISION}/{file_name}"
            digest = hashlib.sha256()
            count = size = 0
            file_rows = []
            req = urllib.request.Request(url, headers={"User-Agent": "codegen-verifier-study-metadata"})
            phase = "request"
            with urllib.request.urlopen(req, timeout=60) as response:
                while True:
                    if time.monotonic() - started > MAX_SECONDS:
                        raise TimeoutError("Census wall-time limit")
                    phase = "read_line"
                    raw = response.readline(MAX_LINE + 1)
                    if not raw:
                        break
                    total += len(raw)
                    phase = "line_size_check"
                    if len(raw) > MAX_LINE:
                        raise ValueError("Line size limit")
                    size += len(raw)
                    phase = "download_size_check"
                    if total > MAX_TOTAL or size > EXPECTED[file_name][0]:
                        raise ValueError("Download size limit")
                    digest.update(raw)
                    # Do not retain the record or inspect any other field.
                    if raw.strip():
                        phase = "metadata_projection"
                        file_rows.append(project(json.loads(raw)))
                        count += 1
                    del raw
            phase = "source_hash_check"
            if (size, digest.hexdigest()) != EXPECTED[file_name]:
                raise ValueError("Pinned source digest/size mismatch")
            source = {"file": file_name, "url": url, "sha256": digest.hexdigest(), "bytes": size, "rows": count}
            sources.append(source)
            rows.extend(file_rows)
            save(cache_name, {"revision": REVISION, "source": source, "rows": file_rows,
                             "projection_sha256": hashlib.sha256(json.dumps(file_rows, sort_keys=True).encode()).hexdigest()})
            print(f"Projected {file_name}: {count} metadata rows", flush=True)
        phase = "census"
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
        manifest.update(status="failed", failed_file=file_name, error_type=type(error).__name__, failure_phase=phase, projected_rows=len(rows))
        # Never serialize exception payloads, response bodies or raw task rows.
        print(f"Metadata census failed: {type(error).__name__}", flush=True)
        raise SystemExit(1) from None
    finally:
        manifest.update(downloaded_bytes=total, wall_seconds=round(time.monotonic() - started, 3))
        save("manifest.json", manifest)


if __name__ == "__main__":
    main()
