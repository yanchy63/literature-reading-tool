# Bootstrap portable Python + deps on Windows WITHOUT requiring a preinstalled Python.
# Usage (from skill directory skills/scientific-paper-reading):
#   .\scripts\bootstrap.ps1
#   .\scripts\bootstrap.ps1 -Force

param(
    [switch]$Force,
    [string]$Version = "3.12.11",
    [string]$Release = "20250808"
)

$ErrorActionPreference = "Stop"
$SkillRoot = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $SkillRoot "runtime"
$PythonDir = Join-Path $RuntimeDir "python"
$Arch = $env:PROCESSOR_ARCHITECTURE
if ($Arch -eq "ARM64") {
    $Target = "aarch64-pc-windows-msvc"
} else {
    $Target = "x86_64-pc-windows-msvc"
}
$Asset = "cpython-$Version+$Release-$Target-install_only.tar.gz"
$Url = "https://github.com/astral-sh/python-build-standalone/releases/download/$Release/$Asset"

$Existing = @(
    (Join-Path $PythonDir "python.exe"),
    (Join-Path $PythonDir "python\python.exe")
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($Existing -and -not $Force) {
    Write-Host "[bootstrap] Found bundled Python: $Existing"
} else {
    New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
    $Tmp = Join-Path $env:TEMP ("spr-python-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
    $Archive = Join-Path $Tmp $Asset
    Write-Host "[bootstrap] Downloading $Url"
    Invoke-WebRequest -Uri $Url -OutFile $Archive -UseBasicParsing

    if (Test-Path $PythonDir) { Remove-Item -Recurse -Force $PythonDir }
    New-Item -ItemType Directory -Force -Path $PythonDir | Out-Null

    # tar.exe is available on Windows 10+
    tar -xzf $Archive -C $Tmp
    $Extracted = Get-ChildItem $Tmp -Directory | Where-Object { $_.Name -ne "." } | Select-Object -First 1
    if (-not $Extracted) { throw "Extract failed: no directory in archive" }
    Copy-Item -Recurse -Force (Join-Path $Extracted.FullName "*") $PythonDir

    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
    $Existing = @(
        (Join-Path $PythonDir "python.exe"),
        (Join-Path $PythonDir "python\python.exe")
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $Existing) { throw "python.exe not found after extract" }
    Write-Host "[bootstrap] Installed: $Existing"
}

# Install skill deps into skill .venv using bundled python
$Setup = Join-Path $SkillRoot "scripts\setup_env.py"
& $Existing $Setup --prefer-bundled --reinstall
if ($LASTEXITCODE -ne 0) {
    Write-Host "[bootstrap] setup_env failed; try: & '$Existing' -m pip install -r requirements.txt"
    exit $LASTEXITCODE
}
Write-Host "[bootstrap] Done. Use the recommended_python from setup_env output."
