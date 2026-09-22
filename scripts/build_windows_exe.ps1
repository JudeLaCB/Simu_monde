[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$entryPoint = Join-Path $projectRoot "scripts\run_viewer.py"
$distPath = Join-Path $projectRoot "dist"
$buildPath = Join-Path $projectRoot "build"
$expectedExecutable = Join-Path $distPath "SimuMonde.exe"

$pyInstallerArguments = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "SimuMonde",
    "--distpath", $distPath,
    "--workpath", (Join-Path $buildPath "pyinstaller"),
    "--specpath", $buildPath,
    $entryPoint
)

& python -m PyInstaller @pyInstallerArguments
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $expectedExecutable -PathType Leaf)) {
    throw "PyInstaller did not produce $expectedExecutable"
}

Write-Output "Built $expectedExecutable"
