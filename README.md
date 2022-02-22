## About
Summoner is a Powershell-based tool for making secure RDP or SSH connections to AWS instances over SSM tunnels.

### What's an SSM tunnel? 
SSM is an agent-based host management service provided by AWS. More information is available <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html">here</a>.The SSM agent comes pre-installed on many Amazon-provided AMIs in the Marketplace. By installing the AWS CLI and the SSM plugin on your local machine, you can build an encrypted tunnel to an Instance and interact with it via the AWS CLI. Taking that concept a step further, you can configure RDP or SSH to run over that tunnel.

<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/demo.png" width=60%>

### Why do you need this? 
Security and stability. The SSM agent running on the instance only needs outbound internet connectivity. **There's no need for the instance to have a public IP or inbound rules in its Security Groups.** If configured as such, the Instance can only be accessed via SSM by a user that has authenticated to the AWS CLI. 

## Installation
Summoner requires AWS CLI and the SSM plugin. If these are not installed, run prepare.ps1.
1. Clone or download this repo
2. Open Powershell as an administrator  
3. Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Run `prepare.ps1` 

## Evocation
To start a session, simply right-click cast.ps1 and select "Run with Powershell." Once authenticated, the script will present a series of prompts and start a session as defined. Note that the Powershell window must remain open for the SSM tunnel to stay up. 

## Troubleshooting
**If you cannot reach the instance via RDP**
- Verify the SSM agent is installed and network requirements are met. 
    1. Select the Instance in the EC2 console
    2. Click "Connect"
    3. Select the "Session Manager" tab 
    4. Review any error messages 
- It can take up to 10 minutes for an Instance to become reachable after launch.
- If you reboot the Instance, you'll need to re-run cast.ps1 so a new SSM tunnel can be built.