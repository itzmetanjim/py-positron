param(
  [Parameter(Mandatory=$true)]
  [string]$Command,
  [Parameter(Mandatory=$true)]
  [string]$Path,
  [Parameter(Mandatory=$true)]
  [string]$pythonExe
)
Set-Location $Path
& $pythonExe $Command
