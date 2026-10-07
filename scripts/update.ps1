# One command to ship an update from this laptop to the live site.
#
#   powershell -ExecutionPolicy Bypass -File scripts\update.ps1
#
# 1. Takes the newest portfolio-update-*.zip from Downloads (or -Zip <path>)
# 2. Unpacks it into the project, commits and pushes to GitHub
# 3. Connects to the server over SSH and runs scripts/deploy.sh
# The processed zip is moved to Downloads\portfolio-applied so it is never applied twice.
param(
    [string]$Zip = "",
    [string]$Server = "root@185.196.215.179",
    [string]$Message = ""
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

function Step($text) { Write-Host "`n-> $text" -ForegroundColor Cyan }

if (-not $Zip) {
    $latest = Get-ChildItem "$HOME\Downloads\portfolio-update-*.zip" -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
        # A zip older than the last commit is a leftover that was applied (or replaced) long ago.
        # Applying it again silently reverts newer files, so it is skipped.
        $headUnix = git log -1 --format=%ct 2>$null
        $headTime = if ($headUnix) { [DateTimeOffset]::FromUnixTimeSeconds([int64]$headUnix).LocalDateTime } else { [DateTime]::MinValue }
        if ($latest.LastWriteTime -lt $headTime) {
            Write-Host "Skipping $($latest.Name): it is older than the last commit ($headTime)." -ForegroundColor Yellow
            Write-Host "Move old zips out of Downloads: Move-Item $HOME\Downloads\portfolio-update-*.zip $HOME\Downloads\portfolio-applied\" -ForegroundColor Yellow
        } else {
            $Zip = $latest.FullName
        }
    }
}

if ($Zip) {
    Step "Unpacking $(Split-Path -Leaf $Zip)"
    Expand-Archive -Path $Zip -DestinationPath . -Force
    $done = "$HOME\Downloads\portfolio-applied"
    New-Item -ItemType Directory -Force -Path $done | Out-Null
    Move-Item -Force $Zip $done
    if (-not $Message) { $Message = "Update: " + [IO.Path]::GetFileNameWithoutExtension($Zip) }
} else {
    Write-Host "No new portfolio-update-*.zip in Downloads - deploying the current code." -ForegroundColor Yellow
}

if (git status --porcelain) {
    Step "Committing and pushing"
    if (-not $Message) { $Message = "Update from laptop" }
    git add -A
    git commit -q -m $Message
}
# Take in commits pushed from another computer first; on a clash our local version wins
git pull -q --rebase -X theirs
if ($LASTEXITCODE -ne 0) { throw "git pull failed - run 'git status' and send me the output" }
git push -q
if ($LASTEXITCODE -ne 0) { throw "git push failed" }

Step "Deploying on the server (you may be asked for the SSH password)"
ssh $Server "cd /srv/portfolio/app && sudo -u portfolio git fetch -q && sudo -u portfolio git show @{u}:scripts/deploy.sh > /tmp/portfolio-deploy.sh && bash /tmp/portfolio-deploy.sh"
if ($LASTEXITCODE -ne 0) { throw "Deploy failed - see the output above" }

Write-Host "`nDone." -ForegroundColor Green
