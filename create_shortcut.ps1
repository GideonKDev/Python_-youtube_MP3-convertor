# create_shortcut.ps1
$exePath = ".\dist\YouTube2MP3.exe"
$shortcutPath = "$env:USERPROFILE\Desktop\YouTube to MP3 Converter.lnk"

if (Test-Path $exePath) {
    # Create shortcut
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = (Resolve-Path $exePath).Path
    $shortcut.WorkingDirectory = (Get-Item $exePath).DirectoryName
    $shortcut.Save()
    
    Write-Host "Shortcut created on desktop!" -ForegroundColor Green
    Write-Host "Shortcut: $shortcutPath" -ForegroundColor Green
} else {
    Write-Host "Executable not found: $exePath" -ForegroundColor Red
    Write-Host "Make sure to build the .exe first" -ForegroundColor Yellow
}

Read-Host "`nPress Enter to exit"