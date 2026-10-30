param(
    [string]$GameDir = "A:\SteamLibrary\steamapps\common\Command & Conquer Generals - Zero Hour",
    [string]$Version = "6.8.0",
    [string]$D3D8To9Version = "1.16.0"
)

$ErrorActionPreference = "Stop"
$work = Join-Path $env:TEMP "tc-reshade"
New-Item -ItemType Directory -Force $work | Out-Null

$setup = Join-Path $work "ReShade_Setup_$Version.exe"
if (-not (Test-Path $setup)) {
    Invoke-WebRequest "https://reshade.me/downloads/ReShade_Setup_$Version.exe" -OutFile $setup -UseBasicParsing -UserAgent "Mozilla/5.0"
}

# The setup is a self-extracting zip; Windows tar reads it, .NET's ZipFile does not.
Push-Location $work
try {
    & "$env:SystemRoot\System32\tar.exe" -xf $setup ReShade32.dll
    if ($LASTEXITCODE -ne 0) { throw "Extracting ReShade32.dll failed" }
} finally {
    Pop-Location
}
# ReShade has no Direct3D 8 entry point. d3d8to9 translates the game to Direct3D 9 as
# d3d8.dll and loads d3d9.dll from the game folder first, which is ReShade.
Copy-Item (Join-Path $work "ReShade32.dll") (Join-Path $GameDir "d3d9.dll") -Force

$d3d8to9 = Join-Path $work "d3d8to9-$D3D8To9Version.dll"
if (-not (Test-Path $d3d8to9)) {
    Invoke-WebRequest "https://github.com/crosire/d3d8to9/releases/download/v$D3D8To9Version/d3d8.dll" -OutFile $d3d8to9 -UseBasicParsing
}
Copy-Item $d3d8to9 (Join-Path $GameDir "d3d8.dll") -Force

$shaders = Join-Path $GameDir "reshade-shaders"
foreach ($repo in @(@{ Url = "https://github.com/crosire/reshade-shaders.git"; Branch = "slim"; Dir = "base" },
                   @{ Url = "https://github.com/martymcmodding/qUINT.git"; Branch = "master"; Dir = "quint" })) {
    $dest = Join-Path $work $repo.Dir
    if (-not (Test-Path $dest)) { git clone -q --depth 1 -b $repo.Branch $repo.Url $dest }
    foreach ($sub in "Shaders", "Textures") {
        if (Test-Path "$dest\$sub") {
            robocopy "$dest\$sub" "$shaders\$sub" /E /NFL /NDL /NJH /NJS | Out-Null
        }
    }
}

Copy-Item "$PSScriptRoot\..\..\Operational\ReShade\TheaterCommand.ini" $GameDir -Force

$ini = Join-Path $GameDir "ReShade.ini"
if (-not (Test-Path $ini)) {
@"
[GENERAL]
EffectSearchPaths=.\reshade-shaders\Shaders\**
TextureSearchPaths=.\reshade-shaders\Textures\**
PresetPath=.\TheaterCommand.ini
PerformanceMode=1

[INPUT]
KeyOverlay=36,0,0,0

[OVERLAY]
TutorialProgress=4
"@ | Set-Content $ini -Encoding ascii
}

Write-Output "Installed d3d8to9 $D3D8To9Version (d3d8.dll) and ReShade $Version (d3d9.dll) in $GameDir (Home opens the overlay)"
