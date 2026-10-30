param(
    [Parameter(Mandatory)][ValidateSet("click", "rclick", "key", "shot", "move", "drag")][string]$Action,
    [int]$X, [int]$Y, [int]$X2, [int]$Y2,
    [string]$Key,
    [string]$Out = (Join-Path $env:TEMP "tc-shot.png"),
    [double]$Scale = 0.5
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class GameInput {
    [StructLayout(LayoutKind.Sequential)] struct MOUSEINPUT { public int dx, dy, mouseData, dwFlags, time; public IntPtr extra; }
    [StructLayout(LayoutKind.Sequential)] struct KEYBDINPUT { public short wVk, wScan; public int dwFlags, time; public IntPtr extra; }
    [StructLayout(LayoutKind.Explicit)] struct INPUT { [FieldOffset(0)] public int type; [FieldOffset(8)] public MOUSEINPUT mi; [FieldOffset(8)] public KEYBDINPUT ki; }
    [DllImport("user32.dll")] static extern uint SendInput(uint n, INPUT[] inputs, int size);
    [DllImport("user32.dll")] static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] static extern uint MapVirtualKey(uint code, uint mapType);
    [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
    public static int ForegroundProcessId() { int p; GetWindowThreadProcessId(GetForegroundWindow(), out p); return p; }
    const int MOUSE = 0, KEYBOARD = 1;
    static void Mouse(int flags) { var i = new INPUT { type = MOUSE }; i.mi.dwFlags = flags; SendInput(1, new[] { i }, Marshal.SizeOf(typeof(INPUT))); }
    public static void Move(int x, int y) { SetCursorPos(x, y); }
    public static void Click(int x, int y, bool right) {
        SetCursorPos(x, y); System.Threading.Thread.Sleep(80);
        Mouse(right ? 0x0008 : 0x0002); System.Threading.Thread.Sleep(60); Mouse(right ? 0x0010 : 0x0004);
    }
    public static void Drag(int x1, int y1, int x2, int y2) {
        SetCursorPos(x1, y1); System.Threading.Thread.Sleep(80); Mouse(0x0002);
        for (int s = 1; s <= 10; s++) { SetCursorPos(x1 + (x2 - x1) * s / 10, y1 + (y2 - y1) * s / 10); System.Threading.Thread.Sleep(30); }
        Mouse(0x0004);
    }
    public static void Key(ushort vk) {
        // Scan codes, because the game reads DirectInput.
        var down = new INPUT { type = KEYBOARD }; down.ki.wVk = (short)vk; down.ki.wScan = (short)MapVirtualKey(vk, 0); down.ki.dwFlags = 0x0008;
        var up = down; up.ki.dwFlags = 0x0008 | 0x0002;
        SendInput(1, new[] { down }, Marshal.SizeOf(typeof(INPUT))); System.Threading.Thread.Sleep(60);
        SendInput(1, new[] { up }, Marshal.SizeOf(typeof(INPUT)));
    }
}
"@

if ($Action -ne "shot") {
    $game = Get-Process generalszh -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $game -or [GameInput]::ForegroundProcessId() -ne $game.Id) {
        throw "The game is not the foreground window; refusing to send input."
    }
}

switch ($Action) {
    "click"  { [GameInput]::Click($X, $Y, $false) }
    "rclick" { [GameInput]::Click($X, $Y, $true) }
    "move"   { [GameInput]::Move($X, $Y) }
    "drag"   { [GameInput]::Drag($X, $Y, $X2, $Y2) }
    "key"    { [GameInput]::Key([uint16][System.Windows.Forms.Keys]$Key) }
    "shot"   {
        $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
        [System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
        $small = New-Object System.Drawing.Bitmap $bmp, ([int]($b.Width * $Scale)), ([int]($b.Height * $Scale))
        $small.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output $Out
    }
}
