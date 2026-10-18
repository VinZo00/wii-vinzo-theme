# Ricostruisce il tema VinZo (.csm) dal menu originale 4.3E.
#   1. estrae il base app  2. decomprime gli archivi .ash con ASH.exe (ThemeMii)
#   3. applica le modifiche (tools/build_vinzo.py)  4. verifica il risultato
param(
    [string]$BaseApp   = "$PSScriptRoot\base\0000009a-v514.app",
    [string]$AshExe    = "$env:USERPROFILE\Documents\Wii\ThemeMii\ASH.exe",
    [string]$Wallpaper = "$PSScriptRoot\assets\background.jpg",
    [string]$Out       = "$PSScriptRoot\build\vinzo_material_dark_4.3E.csm"
)
$ErrorActionPreference = "Stop"
$work = "$PSScriptRoot\work"
$venv = "$PSScriptRoot\.venv"

if (-not (Test-Path "$venv\Scripts\python.exe")) {
    python -m venv $venv
    & "$venv\Scripts\python.exe" -m pip install -q -r "$PSScriptRoot\requirements.txt"
}
$py = "$venv\Scripts\python.exe"

New-Item -ItemType Directory -Force "$work\arc", "$work\preview", (Split-Path $Out) | Out-Null
& $py -I "$PSScriptRoot\tools\extract_base.py" $BaseApp "$work\base"

# ASH.exe scrive <file>.arc accanto al file: lavora dentro work\arc
Get-ChildItem "$work\base\layout\common\*.ash" | ForEach-Object {
    Copy-Item $_.FullName "$work\arc\$($_.Name)" -Force
    Push-Location "$work\arc"
    & $AshExe $_.Name *> $null
    Pop-Location
}

& $py -I "$PSScriptRoot\tools\build_vinzo.py" $BaseApp "$work\arc" $Wallpaper $Out "$work\preview"
& $py -I "$PSScriptRoot\tools\verify_csm.py" $BaseApp $Out "$work\preview"
