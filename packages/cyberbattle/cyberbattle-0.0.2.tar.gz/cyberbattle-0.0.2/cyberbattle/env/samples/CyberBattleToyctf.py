from ..env_generation.cyber_env import CyberBattleEnv
from ...utils.objects_and_global_functions import *

default_allow_rules = [
    FirewallRule("RDP", RulePermission.ALLOW),
    FirewallRule("SSH", RulePermission.ALLOW),
    FirewallRule("HTTPS", RulePermission.ALLOW),
    FirewallRule("HTTP", RulePermission.ALLOW)]

# Network nodes involved in the Capture the flag game
nodes = {
    "Website": Node(
        services=[ListeningService("HTTPS"),
                  ListeningService("SSH", allowedCredentials=[
                      "ReusedMySqlCred-web"])],
        firewall=FirewallConfiguration(incoming=default_allow_rules,
                                       outgoing=default_allow_rules + [
                                           FirewallRule(
                                               "su", RulePermission.ALLOW),
                                           FirewallRule("sudo", RulePermission.ALLOW)]),
        value=100,
        # If can SSH into server then gets FLAG "Shared credentials with
        # database user"
        properties=["MySql", "Ubuntu", "nginx/1.10.3"],
        owned_string="FLAG: Login using insecure SSH user/password",
        vulnerabilities=dict(
            ScanPageContent=VulnerabilityInfo(
                description="LeakedGitHubProjectUrl: Website page content shows a link to GitHub "
                            "repo",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedNodesId(["GitHubProject"]),
                reward_string="WEBSITE page content has a link to github -> Github project discovered!",
                cost=1.0
            ),
            ScanPageSource=VulnerabilityInfo(
                description="Website page source contains refrence to browseable "
                            "relative web directory",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedNodesId(["Website.Directory"]),
                reward_string="Viewing the web page source reveals a URL to a .txt file and directory on the website",
                cost=1.0
            ),
            CredScanBashHistory=VulnerabilityInfo(
                description="bash history leaking creds - FLAG Stealing "
                            "credentials for the monitoring user",
                type=VulnerabilityType.LOCAL,
                outcome=LeakedCredentials(credentials=[
                    CachedCredential(node="Website[user=monitor]", port="SSH",
                                     credential="monitorBashCreds")]),
                reward_string="FLAG: SSH history revealed credentials for the monitoring user (monitor)",
                cost=1.0
            ))),

    "Website.Directory": Node(
        services=[ListeningService("HTTPS")],
        value=50,
        properties=["Ubuntu", "nginx/1.10.3",
                    "CTFFLAG:Readme.txt-Discover secret data"
                    ],
        vulnerabilities=dict(
            NavigateWebDirectoryFurther=VulnerabilityInfo(
                description="Discover MYSQL credentials MySql for user "
                            "'web' in (getting-started.txt)",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedCredentials(credentials=[
                    CachedCredential(node="Website", port="MySQL",
                                     credential="ReusedMySqlCred-web")]),
                reward_string="FLAG: Discover browseable web directory: Navigating to parent URL revealed file `readme.txt`"
                              "with secret data (aflag); and `getting-started.txt` with MYSQL credentials",
                cost=1.0
            ),
            NavigateWebDirectory=VulnerabilityInfo(
                description="Discover URL to external sharepoint website "
                            "(in deprecation-checklist.txt)",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedNodesId(["Sharepoint"]),
                reward_string="Navigating to parent URL revealed file `deprecation-checklist.txt` containing"
                              "a URL to an external sharepoint website",
                cost=1.0
            )
        )),

    "Website[user=monitor]": Node(
        services=[ListeningService("SSH", allowedCredentials=[]),
                  ListeningService(
            "SSH-key", allowedCredentials=["unkownkey"]),
            ListeningService("su", allowedCredentials=["monitorBashCreds"])],
        value=100,
        properties=["MySql", "Ubuntu", "nginx/1.10.3"],
        owned_string="FLAG: User escalation by stealing credentials from bash history",
        firewall=FirewallConfiguration(
            outgoing=default_allow_rules,
            incoming=[FirewallRule("SSH", RulePermission.BLOCK,
                                   reason="password authentication disabled! SSH needs private key to authenticate."),
                      FirewallRule("sudo", RulePermission.BLOCK,
                                   reason="`sudo -u monitor` failed. User 'monitor' not sudoable."
                                   "This warning will be reported!"),
                      FirewallRule("su", RulePermission.ALLOW)] + default_allow_rules
        ),
        vulnerabilities={
            "CredScan-HomeDirectory":
                VulnerabilityInfo(
                    description="azurecredential.txt file in home directory",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedCredentials(credentials=[
                        CachedCredential(
                                node="AzureResourceManager[user=monitor]",
                                port="HTTPS",
                                credential="azuread_user_credentials")]),
                    reward_string="SSH: cat ~/azurecreds.txt (running as monitor) revealed Azure user credential!",
                    cost=1.0),
        }),

    "GitHubProject": Node(
        services=[ListeningService("GIT")],
        value=10,
        properties=["GitHub", "SasUrlInCommit"],
        vulnerabilities=dict(
            CredScanGitHistory=VulnerabilityInfo(
                description="Some secure access token (SAS) leaked in a "
                "reverted git commit",
                type=VulnerabilityType.REMOTE,
                precondition=Precondition('SasUrlInCommit&GitHub'),
                outcome=LeakedCredentials(credentials=[
                    CachedCredential(node="AzureStorage",
                                     port="HTTPS",
                                     credential="SASTOKEN1")]),
                rates=Rates(probingDetectionRate=0.0,
                            exploitDetectionRate=0.0,
                            successRate=1.0),
                reward_string="CredScan success: Some secure access token (SAS) was leaked in a reverted git commit",
                cost=1.0
            ))),

    "AzureStorage": Node(
        services=[
            ListeningService("HTTPS", allowedCredentials=["SASTOKEN1"])],
        value=50,
        properties=["CTFFLAG:LeakedCustomerData"],
        vulnerabilities=dict(
            AccessDataWithSASToken=VulnerabilityInfo(
                description="Stealing secrets using a publicly shared "
                            "SAS token",
                type=VulnerabilityType.REMOTE,
                outcome=CustomerData(),
                rates=Rates(successRate=1.0),
                reward_string="Stole data using a publicly shared SAS token",
                cost=1.0
            )
        )),

    'Sharepoint': Node(
        services=[ListeningService("HTTPS")],
        value=100,
        properties=["SharepointLeakingPassword"],
        firewall=FirewallConfiguration(incoming=[FirewallRule("SSH", RulePermission.ALLOW),
                                                 FirewallRule(
                                                     "HTTP", RulePermission.ALLOW),
                                                 FirewallRule("HTTPS", RulePermission.ALLOW)],
                                       outgoing=[]),
        vulnerabilities=dict(
            ScanSharepointParentDirectory=VulnerabilityInfo(
                description="Navigate to SharePoint site, browse parent "
                            "directory",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedCredentials(credentials=[
                    CachedCredential(node="AzureResourceManager",
                                     port="HTTPS",
                                     credential="ADPrincipalCreds")]),
                rates=Rates(successRate=1.0),
                reward_string="Navigating to the Sharepoint site revealed  AD Service Principal Credentials",
                cost=1.0)
        )),

    'AzureResourceManager': Node(
        services=[
            ListeningService(
                "HTTPS",
                allowedCredentials=[
                    "ADPrincipalCreds",
                    "azuread_user_credentials"])],
        owned_string="FLAG: Shared credentials with database user - Obtained secrets hidden in Azure Managed Resources",
        value=50,
        properties=["CTFFLAG:LeakedCustomerData2"],
        vulnerabilities=dict(
            ListAzureResources=VulnerabilityInfo(
                description="AzureVM info, including public IP address",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedNodesId(["AzureVM"]),
                reward_string="Obtained Azure VM and public IP information",
                cost=1.0
            ))),

    'AzureResourceManager[user=monitor]': Node(
        services=[
            ListeningService(
                "HTTPS",
                allowedCredentials=["azuread_user_credentials"])],
        owned_string="More secrets stolen when logged as interactive `monitor` user in Azure with `az`",
        value=50,
        properties=[],
    ),

    'AzureVM': Node(
        services=[ListeningService("PING"),
                  ListeningService("SSH")],
        value=100,
        properties=["CTFFLAG:VMPRIVATEINFO"],
        firewall=FirewallConfiguration(
            incoming=[FirewallRule("SSH", RulePermission.BLOCK,
                                   reason="internet incoming traffic blocked on the VM by NSG firewall")],
            outgoing=[])),

    'client': Node(
        services=[],
        value=0,
        vulnerabilities=dict(
            SearchEdgeHistory=VulnerabilityInfo(
                description="Search web history for list of accessed websites",
                type=VulnerabilityType.LOCAL,
                outcome=LeakedNodesId(["Website"]),
                reward_string="Web browser history revealed website URL of interest",
                cost=1.0
            )),
        agent_installed=True,
        reimagable=False),
}


def global_vulnerabilities(nodes):

    gv = dict()

    for node in nodes:

        for vulnerability in nodes[node].vulnerabilities:

            if vulnerability not in gv:

                gv[vulnerability] = nodes[node].vulnerabilities[vulnerability]

    return gv


global_vulnerability = global_vulnerabilities(nodes)

Toyctf_IDENTIFIERS = infer_constants_from_nodes(nodes, global_vulnerability)


def new_environment():

    return Environment(
        network=create_network(nodes),
        vulnerability_library=global_vulnerability,
        identifiers=Toyctf_IDENTIFIERS)


class Toyctf_env(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(initial_environment=new_environment(), **kwargs)
