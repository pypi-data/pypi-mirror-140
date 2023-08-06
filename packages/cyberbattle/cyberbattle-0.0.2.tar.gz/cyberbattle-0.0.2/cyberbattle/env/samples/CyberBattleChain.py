from ..env_generation.cyber_env import CyberBattleEnv
from ...utils.objects_and_global_functions import *

# Environment constants used for all instances of the chain network
Chain_IDENTIFIERS = Identifiers(
    properties=[
        'Windows',
        'Linux',
        'ApacheWebSite',
        'IIS_2019',
        'IIS_2020_patched',
        'MySql',
        'Ubuntu',
        'nginx/1.10.3',
        'SMB_vuln',
        'SMB_vuln_patched',
        'SQLServer',
        'Win10',
        'Win10Patched',
        'FLAG:Linux'
    ],
    ports=[
        'HTTPS',
        'SSH',
        'RDP'
    ],
    local_vulnerabilities=[
        'ScanBashHistory',
        'ScanExplorerRecentFiles',
        'SudoAttempt',
        'CrackKeepPassX',
        'CrackKeepPass'
    ],
    remote_vulnerabilities=[
        'ProbeLinux',
        'ProbeWindows'
    ]
)


def prefix(x: int, name: str):
    """Prefix node name with an instance"""
    return f"{x}_{name}"


def rdp_password(index):
    """Generate RDP password for the specified chain link"""
    return f"WindowsPassword!{index}"


def ssh_password(index):
    """Generate SSH password for the specified chain link"""
    return f"LinuxPassword!{index}"


def create_network_chain_link(n):
    """Instantiate one link of the network chain with associated index n"""

    def current(name):
        return prefix(n, name)

    def next(name):
        return prefix(n + 1, name)

    return {
        current("LinuxNode"): Node(
            services=[ListeningService("HTTPS"),
                      ListeningService("SSH", allowedCredentials=[ssh_password(n)])],
            value=100,
            properties=["MySql", "Ubuntu", "nginx/1.10.3"],
            owned_string="Intermediate chain node owned, no intinsic value",
            vulnerabilities=dict(
                ProbeLinux=VulnerabilityInfo(
                    description="Probe to check if the node runs Linux",
                    type=VulnerabilityType.REMOTE,
                    outcome=ProbeSucceeded(["Ubuntu"]),
                    reward_string="Remote machine is running Linux",
                    cost=5.0
                ),
                ProbeWindows=VulnerabilityInfo(
                    description="Probe to check if the node runs Windows",
                    type=VulnerabilityType.REMOTE,
                    outcome=ProbeFailed(),
                    reward_string="Remote machine is not running Windows",
                    cost=5.0
                ),
                ScanBashHistory=VulnerabilityInfo(
                    description="Scan bash history for possible references to other machines",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedNodesId([next("WindowsNode")]),
                    reward_string="Found a reference to a remote Windows node in bash history",
                    cost=1.0
                ),
                ScanExplorerRecentFiles=VulnerabilityInfo(
                    description="Scan Windows Explorer recent files for possible references to other machines",
                    type=VulnerabilityType.LOCAL,
                    outcome=ExploitFailed(),
                    reward_string="Trap: feature not supported on Linux",
                    cost=10.0
                ),
                SudoAttempt=VulnerabilityInfo(
                    description="Attempt to sudo into admin user",
                    type=VulnerabilityType.LOCAL,
                    outcome=ExploitFailed(),
                    reward_string="Trap: suspicious attempt to run sudo",
                    cost=100.0
                ),
                CrackKeepPassX=VulnerabilityInfo(
                    description="Attempt to crack KeepPassX and look for credentials",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedCredentials(credentials=[
                        CachedCredential(node=next("WindowsNode"), port="RDP",
                                         credential=rdp_password(n + 1))]),
                    reward_string=f"Discovered password to Windows machine {n+1}",
                    cost=1.0
                ))),

        next("WindowsNode"): Node(
            services=[ListeningService("HTTPS"),
                      ListeningService("RDP", allowedCredentials=[rdp_password(n + 1)])],
            value=100,
            properties=["Windows", "Win10", "Win10Patched"],
            vulnerabilities=dict(
                ProbeLinux=VulnerabilityInfo(
                    description="Probe to check if the node runs Linux",
                    type=VulnerabilityType.REMOTE,
                    outcome=ProbeFailed(),
                    reward_string="Remote machine is not running Linux",
                    cost=1.0
                ),
                ProbeWindows=VulnerabilityInfo(
                    description="Probe to check if the node runs Windows",
                    type=VulnerabilityType.REMOTE,
                    outcome=ProbeSucceeded(["Windows"]),
                    reward_string="Remote machine is running Windows",
                    cost=1.0
                ),
                ScanBashHistory=VulnerabilityInfo(
                    description="Scan bash history for possible references to other machines",
                    type=VulnerabilityType.LOCAL,
                    outcome=ExploitFailed(),
                    reward_string="Trap: feature not supported on Windows!",
                    cost=100.0
                ),
                ScanExplorerRecentFiles=VulnerabilityInfo(
                    description="Scan Windows Explorer recent files for possible references to other machines",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedNodesId([prefix(n + 2, "LinuxNode")]),
                    reward_string="Found a reference to a remote Linux node in bash history",
                    cost=1.0
                ),
                SudoAttempt=VulnerabilityInfo(
                    description="Attempt to sudo into admin user",
                    type=VulnerabilityType.LOCAL,
                    outcome=ExploitFailed(),
                    reward_string="Trap: feature not supported on Windows!",
                    cost=100.0
                ),
                CrackKeepPassX=VulnerabilityInfo(
                    description="Attempt to crack KeepPassX and look for credentials",
                    type=VulnerabilityType.LOCAL,
                    outcome=ExploitFailed(),
                    reward_string="Trap: feature not supported on Windows!",
                    cost=100.0
                ),
                CrackKeepPass=VulnerabilityInfo(
                    description="Attempt to crack KeepPass and look for credentials",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedCredentials(credentials=[
                        CachedCredential(node=prefix(n + 2, "LinuxNode"), port="SSH",
                                         credential=ssh_password(n + 2))]),
                    reward_string=f"Discovered password to Linux machine {n+2}",
                    cost=1.0
                )
            ))
    }


def create_chain_network(size):
    """Create a chain network with the chain section of specified size.
    Size must be an even number
    The number of nodes in the network is `size + 2` to account for the start node (0)
    and final node (size + 1).
    """

    if size % 2 == 1:
        raise ValueError(f"Chain size must be even: {size}")

    final_node_index = size + 1

    nodes = {
        'start': Node(
            services=[],
            value=0,
            vulnerabilities=dict(
                ScanExplorerRecentFiles=VulnerabilityInfo(
                    description="Scan Windows Explorer recent files for possible references to other machines",
                    type=VulnerabilityType.LOCAL,
                    outcome=LeakedCredentials(
                        credentials=[
                            CachedCredential(
                                node=prefix(
                                    1,
                                    "LinuxNode"),
                                port="SSH",
                                credential=ssh_password(1))]),
                    reward_string="Found a reference to a remote Linux node in bash history",
                    cost=1.0)),
            agent_installed=True,
            reimagable=False),
        prefix(
            final_node_index,
            "LinuxNode"): Node(
            services=[
                ListeningService("HTTPS"),
                ListeningService(
                    "SSH",
                    allowedCredentials=[
                        ssh_password(final_node_index)])],
            value=1000,
            owned_string="FLAG: flag discovered!",
            properties=[
                "MySql",
                "Ubuntu",
                "nginx/1.10.3",
                "FLAG:Linux"],
            vulnerabilities=dict())}

    # Add chain links
    for i in range(1, size, 2):
        nodes.update(create_network_chain_link(i))

    return nodes


def new_environment(size):

    nodes = create_chain_network(size)

    return Environment(
        network=create_network(nodes),
        vulnerability_library=dict([]),
        identifiers=Chain_IDENTIFIERS
    )


class Chain_env(CyberBattleEnv):

    def __init__(self, size, **kwargs):

        self.size = size
        super().__init__(initial_environment=new_environment(size), **kwargs)
