param (
	$Profile = "default", # Update this to your desired profile 
	$Port = (Get-Random -Min 50000 -Max 60000),
	$ErrorActionPreference = "Stop"
)

Write-Host "
 __           
(_     _  _  _  _  _ _ 
__)|_|||||||(_)| )(-|

"

Try {
	Write-Host "Verifying credentials..."
	aws sts get-caller-identity --profile $Profile | Out-Null
	If (!$?) {
		Do {
			Write-host "No valid credentials found. Please update credentials and press ENTER to try again" -Back Black -Fore Yellow -NoNewLine
			Read-Host 
			aws sts get-caller-identity --profile $Profile | Out-Null
		}
		While (!$?)
	}
	$InstanceID = Read-Host "Enter the Instance ID:" 
	$Region = aws configure get region --profile $Profile
	$Overrides = [System.Management.Automation.Host.ChoiceDescription[]] @("&Yes", "&No", "&Cancel")
	$Override = $host.UI.PromptForChoice("Your default region is $Region. Is this where the Instance is?", "", $Choices, 0)
	Switch ($Override) {
		0 {
			Return
		}
		1 {
			$Region = Read-Host "Please enter the region (ex. us-east-1):"
		}
		2 {
			Write-Warning "Operation canceled."
			Exit 0
		}
	}
	$Protocols = [System.Management.Automation.Host.ChoiceDescription[]] @("&RDP", "&SSH", "&Cancel")
	$Protocol = $host.UI.PromptForChoice("Select protocol", "", $Choices, 0)
	Switch ($Protocol) {
		0 {
			Write-Host "Starting RDP session..."
			# Start SSM tunnel in background, so script can continue
			Start-Job -ScriptBlock {
				param ($0 = $Profile, $1 = $InstanceID, $2 = $Region, $3 = $Port) 
				aws ssm start-session --profile $0 --target $1 --region $2 --document-name AWS-StartPortForwardingSession --parameters portNumber="3389",localPortNumber="$3"
			} -ArgumentList ($Profile $InstanceID, $Region, $Port)
			# Wait a few seconds for the SSM tunnel to be built
			Start-Sleep -s 3
			mstsc /v:localhost:$Port
			Write-Warning "This window must remain open for the RDP session."
			Read-Host "Press ENTER to exit"
			Exit 0
		}
		1 {
			$Path = Read-Host "Enter path to the certificate file:"
			$Username = Read-Host "Enter username:"
			Write-Host "Starting SSH session..."
			Start-Job -ScriptBlock {
				param ($0 = $Profile, $1 = $InstanceID, $2 = $Region, $3 = $Port) 
				aws ssm start-session --profile $0 --target $1 --region $2 --document-name AWS-StartPortForwardingSession --parameters portNumber="22",localPortNumber="$3"
			} -ArgumentList ($Profile, $InstanceID, $Region, $Port)
			# Wait a few seconds for the SSM tunnel to be built
			Start-Sleep -s 3
			ssh -i $Path $Username@$InstanceID -p $Port
			# Powershell drops into ssh and script effectively ends
			Exit 0
		}
		2 {
			Write-Warning "Operation canceled."
			Exit 0
		}
	}
}	
Catch {
	Write-Warning "An error occured. `n$_"
    Write-Host "Press ENTER to exit" -Back Black -Fore Yellow -NoNewLine
	Read-Host
	Exit 1 
}