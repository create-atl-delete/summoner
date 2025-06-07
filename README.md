# About
Summoner is a lightweight, VDI-client-like solution for AWS EC2 using AWS SSM. It consists of a simple UI which allows:
- Stopping, starting or restarting Instances
- Initiating connections to Instances over RDP, SSH, or VNC
    - This can be extended to support other protocols

## Packaging
As provided, Summoner is both a complete python package and a set of modules you can use in your own projects. 
1. Summoner (package) - Install with your choice of package manager and start using Summoner right away.
2. Summoner (class) - The full Summoner UI.
3. Evocation (class) - An extension of the SSMPlugin class. Handles starting/stopping the plugin and running a function to establish a connection to the Instance.
4. SSMPlugin (class) - Runs the Session Manager Plugin.

# Prerequisites
## Local Host
### AWS CLI
See install instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions).
### Session Manager Plugin
See install instructions [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).

## Remote Host
### SSM Agent
The SSM agent is pre-installed on almost all AWS Marketplace AMIs. If you are using a custom AMI, see install instructions [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/manually-install-ssm-agent-linux.html).

## IAM Policy
AWS SSM can be enabled at the account level or on individual Instances using an IAM Instance Profile.
### Account
See instructions [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-instance-permissions.html#default-host-management).
### EC2 Instance
See instructions [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-instance-permissions.html#instance-profile-add-permissions).
### User/Role
- To use Evocation or the SSMPlugin modules, users will need the permissions described [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-restrict-access-quickstart.html#restrict-access-quickstart-end-user).
- To use the full Summoner UI, users will also need permissions to start and stop Instances. 

## Networking
### Security Groups
One of the main benefits of AWS SSM is that it requires no inbound access. The Instances' Security Groups do not need any inbound rules in order for Summoner to work.
### VPC Endpoint
For added security, use a VPC Endpoint for AWS SSM See instructions [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-vpc.html). 

# Authentication
Summoner supports most AWS authentication options. Credential expiry will cause any connection to end abrupty, so using long-lived or refreshable credentials is recommended. Summoner supports any credential handler that supports [Credential Provider](https://docs.aws.amazon.com/sdkref/latest/guide/feature-process-credentials.html). Examples include [saml2aws](https://github.com/Versent/saml2aws), [aws-azure-login](https://github.com/aws-azure-login/aws-azure-login), and [aws-vault](https://github.com/99designs/aws-vault).

# Usage
Summoner has several usage modes. In any mode, Summoner will start the Instance if a connection is initiated while it is stopped.
## Config
Use config files for simplified access to a set of Instances using the same AWS Profile/Role. In Config mode, users are presented with a menu from which they can manage their Instances, connect to them, or make changes to the config file. 
## Select
Select from a list of Instances in a specified region. On connection end, Summoner will ask if the Instance can be stopped. 
## Instance
Provide details of an Instance to connect to. On connection end, Summoner will stop the Instance if it started it. Else, it will exit immediately. 

# Custom Connection Types
When using Summoner (class) in your own project, you can add other connection types.

This begins with writing a new connector. See the connectors module for examples. 
- Connectors must accept `**kwargs`.
- Connectors will be passed the Evocation. 

Once a connector has been written, use Summoner.add_connection_type() to add menu options, and config file support.