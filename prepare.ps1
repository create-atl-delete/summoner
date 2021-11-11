<#
    This script will install and configure prerequisites for connect.ps1.
#>

param (
    $Login = "null",
    $USB = "null",
    $Base = ("Amazon\AWSCLIV2", "Amazon\SessionManagerPlugin"),
    $Full = ("Amazon\AWSCLIV2", "Amazon\SessionManagerPlugin", "nodejs", "nodejs\node_modules\npm"),
    $TenantID = "null",
    $AppID = "null",
    $Region = "null"
)

# Check if elevated 
If (!([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Insufficient permissions. Please re-open PowerShell as an administrator and run this script again."
    Read-Host "Press ENTER to exit"
    Exit 1
}

Write-Host "This script may throw errors if any of the applications it attempts to install are already installed. These can be ignored."
$Login = Read-Host "Will you be using aws-azure-login for authentication? (y/n)" 
If ($Login -eq "y") {
    $TenantID = Read-Host "Enter your Azure Tenant ID"
    $AppID = Read-Host "Enter your App ID URL"
    $Region = Read-Host "Enter your default region (ex. us-east-1)"
}
Else {
    Write-host = "Remember to add your temporary credentials to $HOME/.aws/credentials."
}
$USB = Read-Host "Do you want your local machine configured for USB redirection? (y/n)"
If ($USB -eq "y") {
    Write-host "This script will force a reboot upon completion."
}

Write-Host "Creating Restore Point..."
Enable-ComputerRestore -Drive "C:\"
Checkpoint-Computer -Description "Summoner" -RestorePointType "APPLICATION_INSTALL"

# Install and configure chocolatey, then use it to install everything else 
Write-Host "Installing applications with Chocolatey..."
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco feature enable -n allowGlobalConfirmation
choco install openssh
choco install awscli
# Optionally install aws-azure-login
If ($Login -eq "y") {
    choco install nodejs-lts
    # Import refreshenv (a function from chocolatey) so it can be run after the node install 
    Import-Module "C:\ProgramData\chocolatey\helpers\chocolateyProfile.psm1" 
    # The is required to run the npm install 
    refreshenv
    # Install aws-azure-login
    npm install -g aws-azure-login
}

# Install SSM plugin 
Write-Host "Downloading and installing SSM Plugin..."
(New-Object System.Net.WebClient).DownloadFile('https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe',"$HOME\SSMSetup.exe")
Start-Process -FilePath $HOME\SSMSetup.exe -ArgumentList "/S" -NoNewWindow -Wait

# Verify installations
If ($Login -eq "y") { 
    Write-Host "Verifying installations..."
    Foreach ($Path in $Full) {
        If (Test-Path -Path "C:\Program Files\${Path}") {
            Write-Host "${Path} is installed."
        }
        Else {
            Write-Error "${Path} install failed. Please install manually and run this script again."
            Read-Host "Press ENTER to exit"
            Exit 1
        }
    }
}
Else {
    Write-Host "Verifying installations..."
    Foreach ($Path in $Base) {
        If (Test-Path -Path "C:\Program Files\${Path}") {
            Write-Host "${Path} is installed."
        }
        Else {
            Write-Error "${Path} install failed. Please install manually and run this script again."
            Read-Host "Press ENTER to exit"
            Exit 1
        }
    }
}

Write-Host "Cleaning up..."
Remove-Item $HOME\SSMSetup.exe
Write-Host "Installations complete. Proceeding to configuration..."

# Configure aws-azure-login default profile
# If config already exists, make a backup copy - else, make new file 
If ($Login -eq "y") { 
    If (Test-Path $HOME\.aws\config) {
        Copy-Item $HOME\.aws\config $HOME\.aws\config.old
    }
    Else {
        New-Item $HOME\.aws\config -ItemType File -Force
    }
    Set-Content $HOME\.aws\config -Value "[default]
    azure_tenant_id=${TenantID}
    azure_app_id_uri=${AppID}
    region=${Region}"
}

# Optionally configure USB redirect
If ($USB -eq "y") {
    Write-Host "Updating group policy to enable USB Redirection..."
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services\Client" -Name fUsbRedirectionEnableMode -Value 2
    Write-Host "Configuration complete. Your machine will now apply group policy updates and reboot."
    Pause
    gpupdate /force /boot
    Exit 0
}
Else {
    Write-Host "Configuration complete."
    Read-Host "Press ENTER to exit"
    Exit 0
}