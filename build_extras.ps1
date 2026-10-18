# Genera i temi coordinati per Homebrew Channel e USB Loader GX e, se l'unità è collegata, li copia.
#   HBC:  build\hbc\apps\HBCtheme_VinZo        -> D:\apps\HBCtheme_VinZo (aprirla dall'HBC per installare)
#   GX:   build\usbloadergx\vinzo.them + vinzo\ -> D:\apps\usbloader_gx\theme\
# Basi di terzi (non nel repo): third_party\hbc_material_dark (font Roboto), third_party\gx_azurenight.
param([string]$Drive = "D:")
$ErrorActionPreference = "Stop"
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
$tp = "$PSScriptRoot\third_party"
& $py -I "$PSScriptRoot\tools\hbc_theme.py" "$PSScriptRoot\assets\barra.jpg" `
    "$tp\hbc_material_dark\Roboto-Regular.ttf" "$tp\hbc_material_dark\Roboto-Medium.ttf" "$PSScriptRoot\build\hbc"
& $py -I "$PSScriptRoot\tools\gx_theme.py" "$tp\gx_azurenight\azurenight.them" "$tp\gx_azurenight\azurenight" `
    "$PSScriptRoot\assets\barra.jpg" "$PSScriptRoot\build\usbloadergx"
if (Test-Path "$Drive\apps") {
    Copy-Item "$PSScriptRoot\build\hbc\apps\HBCtheme_VinZo" "$Drive\apps\" -Recurse -Force
    Copy-Item "$PSScriptRoot\build\usbloadergx\vinzo.them" "$Drive\apps\usbloader_gx\theme\" -Force
    Copy-Item "$PSScriptRoot\build\usbloadergx\vinzo" "$Drive\apps\usbloader_gx\theme\" -Recurse -Force
    "Copiati su $Drive"
} else { "Unità $Drive non collegata: copia saltata" }
