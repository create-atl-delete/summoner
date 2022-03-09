## About
Summoner is a wrapper around AWS SSM port fowarding functionality. It prompts for an Instance ID, creates a tunnel, and then runs an RDP or SSH session over the tunnel. 

## Prerequisites
Summoner requires AWS CLI and the SSM plugin for AWS CLI.

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