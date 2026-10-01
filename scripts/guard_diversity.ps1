param([Parameter(Mandatory=$true)][int]$GeneratorPid)
$ErrorActionPreference = 'Stop'
$researchRoot = Split-Path -Parent $PSScriptRoot
$researchRun = Join-Path $researchRoot 'runs/mbpp-diversity-budget-development-20261001'
$researchConfig = Get-Content -LiteralPath (Join-Path $researchRoot 'configs/diversity-budget-development.json') -Raw | ConvertFrom-Json
$researchInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$GeneratorPid"
if ($researchInfo.CommandLine -notmatch 'diversity_budget\.py"? generate$') { throw 'Not the expected generation process' }
$researchProcess = Get-Process -Id $GeneratorPid
# Keep a handle to this process instance; a reused PID must never be killed.
$null = $researchProcess.Handle
$researchDeadline = $researchProcess.StartTime.ToUniversalTime().AddSeconds($researchConfig.max_generation_wall_seconds)
$researchRemaining = [Math]::Max(0, [int](($researchDeadline - [DateTime]::UtcNow).TotalMilliseconds))
$researchState = [ordered]@{generator_pid=$GeneratorPid; generator_started_utc=$researchProcess.StartTime.ToUniversalTime().ToString('o'); deadline_utc=$researchDeadline.ToString('o'); script_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLower(); status='watching_actual_generator'; reason='Windows venv launcher has a child interpreter; guard its actual process handle as well as the parent timeout'}
$researchState | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $researchRun 'deadline-guard.json') -Encoding utf8
if (-not $researchProcess.WaitForExit($researchRemaining)) {
    $researchProcess.Kill()
    $researchProcess.WaitForExit()
    $researchState.status='stopped_at_frozen_deadline'
} else {
    $researchState.status='generator_exited_before_deadline'
}
$researchState.finished_utc=[DateTime]::UtcNow.ToString('o')
$researchState | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $researchRun 'deadline-guard.json') -Encoding utf8
