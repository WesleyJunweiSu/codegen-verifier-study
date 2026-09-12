param([Parameter(Mandatory=$true)][int]$ResearchBaseProcessId)
$ErrorActionPreference = 'Stop'
$researchRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $researchRoot
$researchPython = 'C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe'
$researchRun = 'mbpp-routing-v2-development-20260911'
$researchState = Join-Path $researchRoot "runs/$researchRun/queue-state.json"
function Save-ResearchState([string]$State) {
    @{status=$State; updated_utc=[DateTime]::UtcNow.ToString('o'); base_process_id=$ResearchBaseProcessId} |
        ConvertTo-Json | Set-Content -LiteralPath $researchState -Encoding utf8
}
try {
    $researchProcess = Get-Process -Id $ResearchBaseProcessId -ErrorAction SilentlyContinue
    $researchStarted = if ($researchProcess) { $researchProcess.StartTime } else { $null }
    Save-ResearchState 'waiting_for_confirmation_base'
    while ($researchProcess -and $researchProcess.StartTime -eq $researchStarted) {
        Start-Sleep -Seconds 15
        $researchProcess = Get-Process -Id $ResearchBaseProcessId -ErrorAction SilentlyContinue
    }
    $researchBase = 'runs/mbpp-confirmation-20260911'
    if ((Get-Content -LiteralPath "$researchBase/generations.jsonl").Count -ne 720 -or
        (Get-Content -LiteralPath "$researchBase/generated-tests.jsonl").Count -ne 180) {
        throw 'Confirmation base ended before completion; resume it before routing generation.'
    }
    Save-ResearchState 'running_development_extensions'
    & $researchPython -X utf8 scripts/generate_routing_v2.py --model-path 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'
    if ($LASTEXITCODE -ne 0) { throw 'Routing generator failed.' }
    if (-not (Test-Path -LiteralPath "runs/$researchRun/generations.jsonl")) {
        Save-ResearchState 'deferred_gpu_headroom'
        exit 0
    }
    Save-ResearchState 'generation_complete_dispatching'
    & git -c "safe.directory=$researchRoot" add -- "runs/$researchRun"
    if ($LASTEXITCODE -ne 0) { throw 'Input staging failed.' }
    & git -c "safe.directory=$researchRoot" commit -m 'Record completed development routing resamples'
    if ($LASTEXITCODE -ne 0) { throw 'Input commit failed.' }
    & git -c "safe.directory=$researchRoot" push origin HEAD:main
    if ($LASTEXITCODE -ne 0) { throw 'Input push failed.' }
    & $researchPython -X utf8 scripts/github_ops.py dispatch --workflow routing-development.yml --input-run $researchRun
    if ($LASTEXITCODE -ne 0) { throw 'Workflow dispatch failed.' }
    Save-ResearchState 'scoring_dispatched_import_artifacts_next'
} catch {
    Save-ResearchState 'stopped_check_log_before_retry'
    throw
}
