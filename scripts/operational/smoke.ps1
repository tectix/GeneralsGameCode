param(
    [string]$GameDir = "A:\SteamLibrary\steamapps\common\Command & Conquer Generals - Zero Hour",
    [int]$WaitSeconds = 30,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"

Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public static class GameWindows {
    delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc p, IntPtr l);
    [DllImport("user32.dll")] static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
    [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    public static List<string> Titles(int id) {
        var r = new List<string>();
        EnumWindows((h, l) => {
            int p; GetWindowThreadProcessId(h, out p);
            if (p == id && IsWindowVisible(h)) { var s = new StringBuilder(256); GetWindowText(h, s, 256); r.Add(s.ToString()); }
            return true;
        }, IntPtr.Zero);
        return r;
    }
}
"@

$crashLog = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "Command and Conquer Generals Zero Hour Data\ReleaseCrashInfo.txt"
$crashBefore = if (Test-Path $crashLog) { (Get-Item $crashLog).LastWriteTime } else { $null }

$process = Get-Process generalszh -ErrorAction SilentlyContinue | Select-Object -First 1
if ($process -and $Restart) {
    Stop-Process -Id $process.Id -Force
    $process = $null
}
if (-not $process) {
    $process = Start-Process (Join-Path $GameDir "generalszh.exe") -WorkingDirectory $GameDir -PassThru
    Start-Sleep $WaitSeconds
}

$process.Refresh()
if ($process.HasExited) {
    Write-Output "FAIL: game exited with code $($process.ExitCode)"
    exit 1
}

$titles = [GameWindows]::Titles($process.Id)
$crashAfter = if (Test-Path $crashLog) { (Get-Item $crashLog).LastWriteTime } else { $null }

if ($titles.Count -ne 1 -or $titles[0] -match "Technical Difficulties|Error" -or $crashAfter -ne $crashBefore) {
    Write-Output "FAIL: windows: $($titles -join ' | ')"
    if ($crashAfter -ne $crashBefore) { Get-Content $crashLog -TotalCount 20 }
    exit 1
}

Write-Output "OK: $($titles[0])"
