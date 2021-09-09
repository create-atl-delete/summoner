## About
Summoner is a Powershell-based CLI tool for creating secure interactive connections to AWS instances over SSM tunnels.

### What's an SSM tunnel? 
SSM is short for <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html">Systems Manager</a>. It's an agent-based service provided by AWS for managing instances. The SSM agent comes pre-installed on many Windows and Linux AMIs in the AWS Marketplace. By installing the AWS CLI and the SSM plugin on your local machine, you can establish a secure tunnel to an instance and interact with it via the AWS CLI. Taking that concept a step further, you can configure RDP and SSH to route over that tunnel.

<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/demo.png" width=60%>

### Why do I need this? 
Security and stability. The SSM agent running on the instance only needs outbound internet connectivity. **There's no need for the instance to have a public IP or any inbound rules in its Security Groups.** The instance can only be accessed via SSM by a user that has authenticated to the AWS account in which it resides. Depending on your orgnization, the route used by Summoner connections might also be a more direct route.

### But wait, there's more! 
Summoner can also configure your local machine for USB redirection. You can plug in a physical software license dongle (or any other USB device) and route it through RDP to the instance.

<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/redirect.png" width=60%>

## Installation
To get started...
1. Clone or download this repo
2. Open Powershell as admin 
3. Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Run prepare.ps1

Prepare.ps1 will install: 
- openssh 
- aws cli v2 
- session manager plugin 
- (optional) aws-azure-login

It will also:
- create a configuration file for aws-azure-login
- create a configuration file for ssh
- (optional) enable USB redirection

## Evocation
To start a session, simply right-click connect.ps1 and select "Run with Powershell." If you are already authenticated to AWS by way of<a href="https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html">temporary credentials</a>, the script will proceed. Otherwise, it will prompt for login using <a href="https://github.com/sportradar/aws-azure-login">aws-azure-login</a>. Once authenticated, the script prompt for an instance ID and protocol.

If desired, you can edit summoner.rdp to change the audio and video settings.

## Troubleshooting
**If connect.ps1 throws an error**<br>
Ensure that connect.ps1's dependencies have been added to the System/Path environment variables.
1. Click Start
2. Search "env"
3. Hit Enter 
4. Click Environment Variables...
5. Select Path under System Variables
<img src="https://raw.githubusercontent.com/create-atl-delete/summoner/main/images/env.png" width=60%>

6. Select Path under System Variables
7. Click Edit 
8. Confirm that the following are in the list:
    - C:\Program Files\Amazon\SessionManagerPlugin\bin
    - C:\Program Files\Amazon\AWSCLIV2
    - C:\Program Files\nodejs
9. Click New to add them if needed
10. Close all Powershell windows