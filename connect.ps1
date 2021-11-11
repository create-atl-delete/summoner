<#
	This script starts a connection via RDP over SSM to a specified instance
	You must run prepare.ps1 before you can use this script  
#>

param (
	$InstanceID = "null",
	$Path = "null",
	$Username = "administrator",
	$Proto = "rdp",
	$Region = "null"
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
	$InstanceID = Read-Host "Enter the instance ID" 
	# Get default region
	$Region = aws configure get region
	Write-Host "Your default region is $Region."
	$Region = Read-Host "If the instance is in this region, press ENTER. Else, enter the appropriate region (ex. eu-west-2)"
	# If no input, set back to default
	If ($Region.Length -eq 0){
		$Region = aws configure get region
	}
	$Proto = Read-Host "Enter the desired protocol ([rdp]/ssh)"
	# Begin either rdp or ssh connection 
	If ($Proto -eq "ssh") {
		$Path = Read-Host "Enter the path of the certificate file"
		$Username = Read-Host "Enter the username ([administrator]/ec2-user/ubuntu)"
		Write-Host "Starting SSH session..."
		# Launch SSH 
		aws ssm start-session --target $InstanceID --region $Region --document-name AWS-StartSSHSession --parameters portNumber=56789
		# Wait a few seconds for the SSM tunnel to be built
		Start-Sleep -s 5
		ssh -i $Path $Username@$InstanceID -p 56789
		# Powershell drops into ssh and script effectively ends
	}
	Else {
		Write-Host "Creating SSM tunnel..."
		# Start SSM tunnel in background, so script can continue
		Start-Job -ScriptBlock {
			param ($arg1 = $InstanceID, $arg2 = $Region) aws ssm start-session --target $arg1 --region $arg2 --document-name AWS-StartPortForwardingSession --parameters portNumber="3389",localPortNumber="56789"
		} -ArgumentList ($InstanceID, $Region)
		# Wait a few seconds for the SSM tunnel to be built
		Start-Sleep -s 5
		Write-Host "Starting RDP session..."
		# Launch RDP
		mstsc summoner.rdp
		Write-Host "This window must remain open for the RDP session."
    	Read-Host "Press ENTER to exit"
		Exit 0
	}
}	
Catch {
	Write-Error "An error occured. Please try again."
    Read-Host "Press ENTER to exit"
	Exit 1 
}