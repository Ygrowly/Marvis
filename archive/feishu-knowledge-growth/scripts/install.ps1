[CmdletBinding()]
param(
    [ValidateSet("Claude", "Codex", "Both")]
    [string]$Target = "Both",

    [ValidateSet("User", "Project")]
    [string]$Scope = "User",

    [string]$ProjectPath,

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$skillName = "feishu-knowledge-growth"
$sourcePath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$userProfilePath = [Environment]::GetFolderPath("UserProfile")

if ([string]::IsNullOrWhiteSpace($userProfilePath)) {
    throw "无法确定用户目录。"
}

if ($Scope -eq "Project") {
    if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
        throw "使用 -Scope Project 时必须提供 -ProjectPath。"
    }
    $resolvedProject = (Resolve-Path $ProjectPath).Path
}

function Get-SkillDestination {
    param([string]$ToolName)

    if ($Scope -eq "Project") {
        $root = if ($ToolName -eq "Claude") {
            Join-Path $resolvedProject ".claude\skills"
        } else {
            Join-Path $resolvedProject ".codex\skills"
        }
    } elseif ($ToolName -eq "Claude") {
        $root = Join-Path $userProfilePath ".claude\skills"
    } else {
        $codexRoot = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
            Join-Path $userProfilePath ".codex"
        } else {
            $env:CODEX_HOME
        }
        $root = Join-Path $codexRoot "skills"
    }

    return Join-Path $root $skillName
}

$toolNames = switch ($Target) {
    "Claude" { @("Claude") }
    "Codex"  { @("Codex") }
    default  { @("Claude", "Codex") }
}

$destinations = @{}
foreach ($toolName in $toolNames) {
    $destination = Get-SkillDestination -ToolName $toolName
    $destinations[$toolName] = $destination

    if ((Test-Path $destination) -and -not $Force) {
        throw "目标已存在：$destination。确认升级后重新运行并添加 -Force。"
    }

    if ([IO.Path]::GetFullPath($destination).TrimEnd('\') -eq $sourcePath.TrimEnd('\')) {
        throw "源目录与目标目录相同：$destination"
    }
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($toolName in $toolNames) {
    $destination = $destinations[$toolName]
    $destinationRoot = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null

    $backupPath = $null
    if (Test-Path $destination) {
        $backupPath = "$destination.backup-$timestamp"
        Move-Item -Path $destination -Destination $backupPath
    }

    try {
        New-Item -ItemType Directory -Path $destination | Out-Null
        Get-ChildItem -Path $sourcePath -Force |
            Where-Object { $_.Name -notin @(".git", ".DS_Store") -and $_.Extension -ne ".zip" } |
            Copy-Item -Destination $destination -Recurse -Force
    } catch {
        if (Test-Path $destination) {
            Remove-Item -Path $destination -Recurse -Force
        }
        if ($backupPath -and (Test-Path $backupPath)) {
            Move-Item -Path $backupPath -Destination $destination
        }
        throw
    }

    Write-Host "[$toolName] 已安装到 $destination"
    if ($backupPath) {
        Write-Host "[$toolName] 旧版本已备份到 $backupPath"
    }
}

Write-Host "安装完成。首次使用前请阅读 INSTALL.md 并运行 scripts\bootstrap.ps1 预演。"
