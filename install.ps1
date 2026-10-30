# 文献阅读工具 — 全 Agent 一键安装（Windows）
# 用法:
#   已在仓库内:  .\install.ps1
#   远程一键:    irm https://raw.githubusercontent.com/yanchy63/literature-reading-tool/main/install.ps1 | iex
#   参数:        .\install.ps1 -WithEnv -FetchPython -CursorPlugin

param(
    [switch]$WithEnv,
    [switch]$FetchPython,
    [switch]$CursorPlugin,
    [switch]$Project,
    [string]$Agents = "agents,cursor,claude,codex",
    [string]$RepoUrl = "https://github.com/yanchy63/literature-reading-tool.git",
    [string]$InstallDir = ""
)

$ErrorActionPreference = "Stop"

function Find-Python {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        foreach ($flag in @("-3.12", "-3.11", "-3.10", "-3")) {
            try {
                $exe = & py $flag -c "import sys; print(sys.executable)" 2>$null
                if ($exe) { $candidates += $exe.Trim() }
            } catch {}
        }
    }
    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += $cmd.Source }
    }
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) { return $c }
    }
    return $null
}

# Resolve repo root: script dir if present, else clone
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    # Piped iex: download to temp / clone
    $ScriptDir = ""
}

$RepoRoot = $null
if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "install_agent_skill.py"))) {
    $RepoRoot = $ScriptDir
} elseif (Test-Path ".\install_agent_skill.py") {
    $RepoRoot = (Resolve-Path ".").Path
} else {
    if (-not $InstallDir) {
        $InstallDir = Join-Path $HOME "literature-reading-tool"
    }
    if (-not (Test-Path (Join-Path $InstallDir "install_agent_skill.py"))) {
        Write-Host "[install] Cloning $RepoUrl -> $InstallDir"
        if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
        git clone --depth 1 $RepoUrl $InstallDir
    }
    $RepoRoot = $InstallDir
}

Set-Location $RepoRoot
Write-Host "[install] Repo: $RepoRoot"

$py = Find-Python
$argList = @("install_agent_skill.py", "--agents", $Agents)
if ($Project) { $argList += "--project" }
if ($CursorPlugin) { $argList += "--cursor-plugin" }
if ($WithEnv) { $argList += "--with-env" }
if ($FetchPython) { $argList += "--fetch-python" }

if ($py) {
    Write-Host "[install] Using Python: $py"
    & $py @argList
    exit $LASTEXITCODE
}

# No Python: copy skill dirs with PowerShell only
Write-Host "[install] No Python found; copying skill folders directly..."
$src = Join-Path $RepoRoot "skills\scientific-paper-reading"
if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
    throw "Skill source missing: $src"
}
$targets = @(
    (Join-Path $HOME ".agents\skills\scientific-paper-reading"),
    (Join-Path $HOME ".cursor\skills\scientific-paper-reading"),
    (Join-Path $HOME ".claude\skills\scientific-paper-reading"),
    (Join-Path $HOME ".codex\skills\scientific-paper-reading")
)
$want = $Agents.Split(",") | ForEach-Object { $_.Trim() }
$map = @{
    "agents" = $targets[0]
    "cursor" = $targets[1]
    "claude" = $targets[2]
    "codex"  = $targets[3]
}
foreach ($k in $want) {
    if (-not $map.ContainsKey($k)) { continue }
    $dest = $map[$k]
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
    Copy-Item -Recurse $src $dest
    Write-Host "[install] $k -> $dest"
}

Write-Host "[install] Skill files copied. For Python runtime run:"
Write-Host "  cd $($targets[0]); .\scripts\bootstrap.ps1"
if ($WithEnv) {
    $primary = $targets[0]
    if (Test-Path $primary) {
        Set-Location $primary
        if (Test-Path ".\scripts\bootstrap.ps1") {
            & .\scripts\bootstrap.ps1
        }
    }
}
Write-Host "[install] Done. Repo: https://github.com/yanchy63/literature-reading-tool"
