"""Use the existing Git Credential Manager session without printing credentials."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

REPO = "WesleyJunweiSu/codegen-verifier-study"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["dispatch", "runs", "artifacts", "download", "verify"])
    parser.add_argument("--workflow", default="linux-eval.yml")
    parser.add_argument("--run-id")
    parser.add_argument("--artifact-id")
    parser.add_argument("--output")
    parser.add_argument("--input-run", default="historical-holdout")
    args = parser.parse_args()
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                            capture_output=True, text=True, env=env, check=True)
    credential = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    headers = {"Authorization": "Bearer " + credential["password"], "Accept": "application/vnd.github+json", "User-Agent": "Codex-research"}

    def request(path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request("https://api.github.com/repos/" + REPO + path, data=data,
                                     headers={**headers, "Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else {"status":response.status}

    if args.operation == "dispatch":
        print(request(f"/actions/workflows/{args.workflow}/dispatches", {"ref":"main","inputs":{"input_run":args.input_run}}))
    elif args.operation == "runs":
        data = request("/actions/runs?per_page=5")
        print(json.dumps([{key:run[key] for key in ["id","status","conclusion","html_url","head_sha","created_at"]} for run in data["workflow_runs"]], indent=2))
    elif args.operation == "artifacts":
        data=request(f"/actions/runs/{args.run_id}/artifacts")
        print(json.dumps([{key:item[key] for key in ["id","name","size_in_bytes","expired"]} for item in data["artifacts"]],indent=2))
    elif args.operation == "download":
        assert args.artifact_id and args.output
        # GitHub's API redirects to a time-limited artifact URL. Do not forward authentication across hosts.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                return None
        opener=urllib.request.build_opener(NoRedirect)
        req=urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/artifacts/{args.artifact_id}/zip",headers=headers)
        try:
            with opener.open(req,timeout=60) as response: content=response.read()
        except urllib.error.HTTPError as error:
            if error.code != 302: raise
            with urllib.request.urlopen(error.headers["Location"],timeout=60) as response: content=response.read()
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        Path(args.output).write_bytes(content)
        print("Downloaded artifact bytes:",len(content))
    else:
        data=request("")
        print(json.dumps({key:data[key] for key in ["full_name","private","default_branch","html_url"]}))


if __name__ == "__main__":
    main()
