# Helper to commit and push week-05 to GitHub
# Usage: Right-click -> Run in PowerShell, or run from repo root:
#   .\git_push_week05.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Repo root: $repoRoot"

# Remote repo URL
$remoteUrl = 'https://github.com/nishchal1110/IIIT-HYD.git'
$branch = 'main'

# Ensure we're in the repo root
Push-Location $repoRoot
try {
    # Ensure git is available
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "git is not installed or not on PATH. Install git before running this script."
        exit 1
    }

    # Set remote
    try { git remote remove origin 2>$null } catch { }
    git remote add origin $remoteUrl

    # Add changes
    git add week-05

    # Commit if there are staged changes
    $status = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "No changes to commit in 'week-05'." -ForegroundColor Yellow
    } else {
        git commit -m "Add week-05: YOLO helpers, run_pipeline, Colab notebook"
        Write-Host "Committed changes." -ForegroundColor Green
    }

    # Ensure branch
    git branch -M $branch

    # Push
    Write-Host "Pushing to $remoteUrl (branch $branch) ..."
    git push -u origin $branch
    Write-Host "Push completed." -ForegroundColor Green
} catch {
    Write-Error "Push failed: $_"
    Write-Host "If authentication failed, run 'gh auth login' or use a Personal Access Token (PAT) for HTTPS authentication." -ForegroundColor Yellow
    exit 1
} finally {
    Pop-Location
}
