# Quantum Intel Platform Startup
# Reads services.json — add new DBs/services there, not here.
param([switch]$NoBrowser)

$ErrorActionPreference = "Continue"
$cfg = Get-Content (Join-Path $PSScriptRoot "services.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$svcs = $cfg.services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Quantum Intel Platform Startup ($($svcs.Count) services)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ok = 0; $total = $svcs.Count

for ($i = 0; $i -lt $total; $i++) {
    $s = $svcs[$i]
    Write-Host "[$($i+1)/$total] $($s.name) ..." -ForegroundColor Yellow

    # ── Already running? ──
    $running = $false
    if ($s.check.type -eq "tcp") {
        $ln = netstat -ano 2>$null | Select-String ":$($s.check.port).*LISTENING"
        if ($ln) {
            if ($s.verify) {
                $v = cmd /c $s.verify 2>&1
                if ($LASTEXITCODE -eq 0) { $running = $true }
            } else {
                $running = $true
            }
        }
    }

    if ($running) {
        Write-Host "  Already running" -ForegroundColor Green
        $ok++; continue
    }

    # ── Kill stale app listeners ──
    if ($s.is_app -and $s.port) {
        netstat -ano 2>$null | Select-String ":$($s.port).*LISTENING" | ForEach-Object {
            $kpid = ($_ -split '\s+')[-1]
            Stop-Process -Id $kpid -Force -ErrorAction SilentlyContinue
            Write-Host "  Killed stale PID $kpid"
        }
        Start-Sleep 2
    }

    # ── Start ──
    Write-Host "  Starting ..."
    $pa = @{ FilePath = $s.start.exe; WindowStyle = "Hidden" }
    if ($s.start.args) { $pa.ArgumentList = $s.start.args }
    if ($s.start.cwd)  { $pa.WorkingDirectory = $s.start.cwd }
    Start-Process @pa

    # ── Wait ──
    $ready = $false
    for ($w = 1; $w -le $s.wait_seconds; $w++) {
        Start-Sleep 1
        if ($s.check.type -eq "tcp") {
            $ln = netstat -ano 2>$null | Select-String ":$($s.check.port).*LISTENING"
            if ($ln) {
                if ($s.verify) {
                    $v = cmd /c $s.verify 2>&1
                    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
                } else {
                    $ready = $true; break
                }
            }
        }
        Write-Host "  ... $w/$($s.wait_seconds)s"
    }

    if ($ready) {
        Write-Host "  OK" -ForegroundColor Green
        if ($s.url -and -not $NoBrowser) { Start-Process $s.url }
        $ok++
    } else {
        Write-Host "  [FAIL] Timeout" -ForegroundColor Red
        if ($s.fatal) {
            Write-Host "  Fatal: cannot proceed without $($s.name)" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "========================================" -ForegroundColor Cyan
$color = if ($ok -eq $total) { "Green" } else { "Yellow" }
Write-Host "  $ok/$total ready" -ForegroundColor $color
Write-Host "========================================" -ForegroundColor Cyan
