param(
    [string]$GameDir = "A:\SteamLibrary\steamapps\common\Command & Conquer Generals - Zero Hour",
    [string]$BuildDir = "$PSScriptRoot\..\..\build\win32\GeneralsMD\Release"
)

$ErrorActionPreference = "Stop"

foreach ($name in "generalszh", "WorldBuilderZH", "W3DViewZH") {
    Copy-Item "$BuildDir\$name.exe", "$BuildDir\$name.pdb" $GameDir
}

robocopy "$PSScriptRoot\..\..\Operational\Data" "$GameDir\Data" /E /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copying operational data failed with robocopy code $LASTEXITCODE" }
