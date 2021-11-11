## About
Summoner is a Powershell-based tool for creating secure interactive connections to AWS instances over SSM tunnels.

### What's an SSM tunnel? 
SSM is short for Systems Manager. It's an agent-based service provided by AWS for managing instances. More information is available <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html">here</a>.The SSM agent comes pre-installed on many Amazon-provided AMIs in the AWS Marketplace. By installing the AWS CLI and the SSM plugin on your local machine, you can build an encrypted tunnel to an instance and interact with it via the AWS CLI. Taking that concept a step further, you can configure RDP and SSH to route over that tunnel.

<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/demo.png" width=60%>

### Why do you need this? 
Security and stability. The SSM agent running on the instance only needs outbound internet connectivity. **There's no need for the instance to have a public IP or any inbound rules in its Security Groups.** If configured as such, the instance can only be accessed via SSM by a user that has authenticated to the AWS account in which the instance resides. Depending on your orgnization, the route taken by Summoner connections might be more direct.

### But wait, there's more! 
Summoner can also configure your local machine for USB redirection. You can plug in a physical software license dongle (or any other USB device) and route it through RDP to the instance.

<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/redirect.png" width=60%>

## Installation
Summoner is only available for Windows at this time. It has been tested on Windows 10 and Server 2019.

To get started...
1. Clone or download this repo
2. Open Powershell as an administrator  
3. Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Run prepare.ps1

Prepare.ps1 will install: 
- openssh 
- aws cli v2 
- session manager plugin 
- (optional) aws-azure-login

It will also:
- create a configuration file for ssh
- (optional) create a configuration file for aws-azure-login
- (optional) enable USB redirection

## Evocation
To start a session, simply right-click connect.ps1 and select "Run with Powershell." If you are already authenticated to AWS by way of <a href="https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html">temporary credentials</a>, the script will proceed. Else, it will assume you use <a href="https://github.com/sportradar/aws-azure-login">aws-azure-login</a> and launch a login GUI. Once authenticated, the script will present a series of prompts and start an interactive session as defined. Note that the Powershell window must remain open for the SSM tunnel to stay up. 

If desired, you can edit summoner.rdp to change the audio and video settings.

## Troubleshooting
**If you cannot reach the instance via RDP**
- It can take up to 10 minutes for an instance to become reachable after launch.
- If you reboot the instance, you'll need to re-run connect.ps1 so a new SSM tunnel can be created. 

**If you cannot authenticate to the instance**
- Ensure that the credentials provided to the RDP client are for a configured user on the instance as opposed to a domain user. You may have to enter ".\Administrator" instead of just "Adminstrator" to get RDP to stop trying to use a domain user. 

**If you don't have the option for USB redirection** 
- Confirm that the default client for RDP on your machine is Remote Desktop Connection and not the new Remote Desktop App.

## Troubleshooting
**If connect.ps1 throws an error**<br>
Ensure that connect.ps1's dependencies have been added to the System/Path environment variables.
1. Click Start
2. Search "env"
3. Hit Enter 
4. Click Environment Variables...
5. Select Path under System Variables
6. Click Edit 
7. Confirm that the following are in the list:
    - C:\Program Files\Amazon\SessionManagerPlugin\bin
    - C:\Program Files\Amazon\AWSCLIV2
    - C:\Program Files\nodejs (if using aws-azure-login)
8. Click New to add them if needed
9. Close all Powershell windows