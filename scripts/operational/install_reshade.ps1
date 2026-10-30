param(
    [string]$GameDir = "A:\SteamLibrary\steamapps\common\Command & Conquer Generals - Zero Hour",
    [string]$Version = "6.8.0"
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
Copy-Item (Join-Path $work "ReShade32.dll") (Join-Path $GameDir "d3d8.dll") -Force

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

Write-Output "ReShade $Version installed as d3d8.dll in $GameDir (Home opens the overlay)"
