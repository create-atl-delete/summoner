<#
	This script starts a connection via RDP over SSM to a specified instance
	You must run prepare.ps1 before you can use this script  
#>

param (
	$InstanceID = "null",
	$Path = "null",
	$Username = "administrator",
	$Proto = "rdp"
)

Write-Host " __                    
(_     _  _  _  _  _ _ 
__)|_|||||||(_)| )(-|"

Try {
	# Check if already authenticated 
	Write-Host "Checking if authenticated..."
	aws sts get-caller-identity | Out-Null
	# If last command was unsuccessful (user is unauthenticated) drop into a loop and run aws-azure-login 'till check is successful 
	If (!$?) {
		Do {
			Write-Host "No valid temporary credentials found. Authenticating with aws-azure-login..."
			aws-azure-login --mode gui
			aws sts get-caller-identity | Out-Null
		}
		While (!$?)
	}
	Write-Host "Authentcated."
	# Begin either rdp or ssh connection 
	$InstanceID = Read-Host "Enter the instance ID" 
	$Proto = Read-Host "Enter the desired protocol ([rdp]/ssh)"
	If ($Proto -eq "ssh") {
		$Path = Read-Host "Enter the path of the certificate file"
		$Username = Read-Host "Enter the username ([administrator]/ec2-user/ubuntu)"
		Write-Host "Starting SSH session..."
		# Launch SSH 
		ssh -i $Path $Username@$InstanceID
		# Powershell window is hijacked for ssh and script effectively ends
	}
	Else {
		Write-Host "Creating SSM tunnel..."
		# Start SSM tunnel in background, so script can continue
		Start-Job -ScriptBlock {
			param ($arg1 = $InstanceID) aws ssm start-session --target $arg1 --document-name AWS-StartPortForwardingSession --parameters portNumber="3389",localPortNumber="56789"
		} -ArgumentList $InstanceID
		# Wait a few seconds for the SSM tunnel to be built
		Start-Sleep -s 3
		Write-Host "Starting RDP session..."
		# Launch RDP to localhost
		mstsc summoner.rdp
		Write-Host "This window must remain open for the RDP session."
		Write-Host -NoNewLine "Press any key to exit..."; $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
		Exit 0
	}
}	
Catch {
	Write-Error "An error occured. Please try again."
	Write-Host -NoNewLine "Press any key to exit..."; $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
	Exit 1 
}