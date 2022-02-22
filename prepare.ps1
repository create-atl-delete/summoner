<#
    This script will install and configure prerequisites for connect.ps1.
#>

$Cleanup = 0

# Install AWS CLI 
If (!(Test-Path C:\Program Files\Amazon\AWSCLIV2)) {
    $Cleanup = 1
    Write-Host "Downloading and installing AWS CLI..."
    (New-Object System.Net.WebClient).DownloadFile('https://awscli.amazonaws.com/AWSCLIV2.msi', "$HOME\summoner_temp\CLI.exe")
    Start-Process -FilePath $HOME\CLI.exe -ArgumentList "/S" -NoNewWindow -Wait
}
# Install SSM plugin 
If (!(Test-Path C:\Program Files\Amazon\SessionManagerPlugin)) {
    $Cleanup = 1
    Write-Host "Downloading and installing SSM Plugin..."
    (New-Object System.Net.WebClient).DownloadFile('https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe', "$HOME\summoner_temp\SSM.exe")
    Start-Process -FilePath $HOME\SSM.exe -ArgumentList "/S" -NoNewWindow -Wait
}
If ($Cleanup) { Remove-Item $HOME\summoner_temp\ -Recurse } 

# Optionally configure USB redirect
$USB = Read-Host "Do you want to configure your machine for USB redirection? (y/n):"
Switch ($USB) {
    y {
        Write-Host "Updating group policy to enable USB Redirection..."
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\Client" -Name fUsbRedirectionEnableMode -Value 2
        gpupdate /force
    }
    n {
        Continue
    }
    default {
        Write-Warning "Please enter either y or n."
    }
    Write-Host "Prerequisite tasks complete."
    Read-Host "Press ENTER to exit"
    Exit 0
}