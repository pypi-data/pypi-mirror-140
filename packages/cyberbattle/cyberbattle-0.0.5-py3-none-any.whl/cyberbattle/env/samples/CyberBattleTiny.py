from ..env_generation.cyber_env import CyberBattleEnv
from ...utils.objects_and_global_functions import *

default_allow_rules = [
    FirewallRule("SSH", RulePermission.ALLOW),
]

# Network nodes involved in the Capture the flag game
nodes = {
    "Website": Node(
        services=[
            ListeningService("SSH", allowedCredentials=[
                "ReusedMySqlCred-web"])],
        firewall=FirewallConfiguration(incoming=default_allow_rules,
                                       outgoing=default_allow_rules + [
                                           FirewallRule("su", RulePermission.ALLOW),
                                           FirewallRule("sudo", RulePermission.ALLOW)]),
        value=1000,
        properties=["MySql", "Ubuntu", "nginx/1.10.3"],
        owned_string="FLAG: Login using insecure SSH user/password",
        vulnerabilities=dict(
            ScanPageSource=VulnerabilityInfo(
                description="Website page source contains refrence to browseable "
                            "relative web directory",
                type=VulnerabilityType.REMOTE,
                outcome=LeakedNodesId(["Website.Directory"]),
                reward_string="Viewing the web page source reveals a URL to a .txt file and directory on the website",
                cost=1.0
            ),
        )),

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
                reward_string="Discover browseable web directory: Navigating to parent URL revealed file `readme.txt`"
                              "with secret data (aflag); and `getting-started.txt` with MYSQL credentials",
                cost=1.0
            ),
        )),


    'client': Node(
        services=[],
        properties=["CLIENT:Win10"],
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

Tiny_IDENTIFIERS = infer_constants_from_nodes(nodes, global_vulnerability)


def new_environment():

    return Environment(
        network=create_network(nodes),
        vulnerability_library=global_vulnerability,
        identifiers=Tiny_IDENTIFIERS)


class Tiny_env(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(initial_environment=new_environment(), **kwargs)
