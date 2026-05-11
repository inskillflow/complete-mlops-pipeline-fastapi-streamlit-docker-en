param(
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    Write-Error "No .git directory found in current folder. Run this script from your repository root."
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = "chore: update files $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}

git add -A

$hasChanges = (git status --porcelain)
if (-not $hasChanges) {
    Write-Host "No changes to commit."
    exit 0
}

git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$branch = git rev-parse --abbrev-ref HEAD
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) {
    Write-Error "Unable to determine current branch."
    exit 1
}

git rev-parse --abbrev-ref --symbolic-full-name "@{u}" *> $null
if ($LASTEXITCODE -eq 0) {
    git push
}
else {
    git push -u origin $branch
}
