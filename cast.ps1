<#
	This script starts a connection via RDP over SSM to a specified instance
#>

param (
	$InstanceID = "null",
	$Path = "null",
	$Username = "administrator",
	$Protocol = "rdp",
	$Port = Get-Random -Min 50000 -Max 60000
	$Region = "null"
)

Write-Host "
 __           
(_     _  _  _  _  _ _ 
__)|_|||||||(_)| )(-|
"

Try {
	# Check if already authenticated 
	Write-Host "Verifying credentials..."
	aws sts get-caller-identity | Out-Null
	# If last command was unsuccessful (user is unauthenticated) drop into a loop and run aws-azure-login 'till check is successful 
	If (!$?) {
		Do {
			Read-host "No valid credentials found. Please correct and press ENTER to try again:" 
			aws sts get-caller-identity | Out-Null
		}
		While (!$?)
	}
	$InstanceID = Read-Host "Enter the Instance ID:" 
	$Region = aws configure get region
	$Override = Write-Host "Your default region is $Region. Is this where the Instance is? (y/n)"
	Switch ($Override) {
		y {
			Continue
		}
		n {
			$Region = Read-Host "Please enter the region (ex. us-east-1):"
		}
		default {
			Write-Warning "Invalid response. Please enter either y or n."
		}
	}
	$Protocol = Read-Host "Enter the desired protocol (rdp/ssh):"
	Switch ($Protocol) {
		ssh {
			$Path = Read-Host "Enter the path of the certificate file:"
			$Username = Read-Host "Enter the username:"
			Write-Host "Starting SSH session..."
			aws ssm start-session --target $InstanceID --region $Region --document-name AWS-StartSSHSession --parameters portNumber=$Port
			# Wait a few seconds for the SSM tunnel to be built
			Start-Sleep -s 5
			ssh -i $Path $Username@$InstanceID -p $Port
			# Powershell drops into ssh and script effectively ends
		}
		rdp {
			Write-Host "Starting RDP session..."
			# Start SSM tunnel in background, so script can continue
			Start-Job -ScriptBlock {
				param ($arg1 = $InstanceID, $arg2 = $Region) 
				aws ssm start-session --target $arg1 --region $arg2 --document-name AWS-StartPortForwardingSession --parameters portNumber="3389", localPortNumber="$Port"
			} -ArgumentList ($InstanceID, $Region)
			# Wait a few seconds for the SSM tunnel to be built
			Start-Sleep -s 5
			mstsc /v:localhost:$Port
			Write-Host "This window must remain open for the RDP session."
			Read-Host "Press ENTER to exit:"
			Exit 0
		}
		default {
			Write-warning "Invalid response. Please enter either rdp or ssh."
		}
	}
}	
Catch {
	Write-Error "An error occured. Please try again."
    Read-Host "Press ENTER to exit"
	Exit 1 
}