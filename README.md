## About
Summoner is a Powershell-based tool for RDP or SSH sessions to AWS instances over SSM tunnels.

### What's an SSM tunnel? 
SSM is a host management service provided by AWS. More information is available <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html">here</a>.The SSM agent comes pre-installed on many Amazon-provided AMIs in the Marketplace. By installing the AWS CLI and the SSM plugin on your local machine, you can build an encrypted tunnel to an Instance and interact with it via the AWS CLI. Taking that concept a step further, you can configure RDP or SSH to route over that tunnel.

### What's the benefit? 
Security and stability. The SSM agent running on the instance only needs outbound internet connectivity. **There's no need for the instance to have a public IP or inbound rules in its Security Groups.** If configured as such, the Instance can only be accessed via SSM by a user that has authenticated to the AWS CLI. Depending on your network, the route SSM takes may also be more direct. 

## Installation
Summoner requires AWS CLI and the SSM plugin. If they are not already installed, you can run prepare.ps1 to install both and optionally configure your host for USB redirection.
1. Clone or download this repo
2. Open Powershell as an administrator  
3. `Set-ExecutionPolicy Bypass -Force`
4. `prepare.ps1` 



## Evocation
To start a session, simply right-click cast.ps1 and select "Run with Powershell." Note that the Powershell window must remain open for the SSM tunnel to stay up. 

## Troubleshooting
**If you cannot reach the instance via RDP**
- Verify the SSM agent is installed and network requirements are met. 
    1. Select the Instance in the EC2 console
    2. Click "Connect"
    3. Select the "Session Manager" tab 
    4. Review any error messages 
- If you reboot the Instance, you'll need to re-run cast.ps1 so a new SSM tunnel can be built.