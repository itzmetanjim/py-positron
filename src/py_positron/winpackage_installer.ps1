param(
  [Parameter(Mandatory=$true)]
  [string]$PackageName,
  [Parameter(Mandatory=$true)]
  [string]$Path,
  [Parameter(Mandatory=$false)]
  [bool]$Update = $false
)
Set-Location $Path
$venvDir   = Join-Path $Path 'winvenv'
$pythonExe = Join-Path $venvDir 'Scripts\python.exe'

if (-not (Test-Path $pythonExe)) {
  Write-Error "python.exe not found under '$venvDir'."
  exit 1
}

if ($Update) {
  & $pythonExe -m pip install --upgrade $PackageName
} else {
  & $pythonExe -m pip install $PackageName
}
# Check if the installation was successful
if ($LASTEXITCODE -ne 0) {
  Write-Error "Failed to install/update '$PackageName'."
  exit $LASTEXITCODE
}