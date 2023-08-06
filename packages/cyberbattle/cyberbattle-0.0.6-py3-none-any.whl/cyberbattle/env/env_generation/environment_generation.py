"""Generate a environment randomly."""

import random
import re

from gym.envs.registration import registry, EnvSpec
from ...utils.objects_and_global_functions import *

ADMINTAG = PrivilegeLevel.Admin
SYSTEMTAG = PrivilegeLevel.System

potential_windows_vulns = {
    "UACME43":
    VulnerabilityInfo(
        description="UACME UAC bypass #43",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/hfiref0x/UACME",
        precondition=Precondition(f"Windows&(Win10|Win7)&(~({ADMINTAG}|{SYSTEMTAG}))"),
        outcome={'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(0, 0.2, 1.0)),
    "UACME45":
    VulnerabilityInfo(
        description="UACME UAC bypass #45",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/hfiref0x/UACME",
        precondition=Precondition(f"Windows&Win10&(~({ADMINTAG}|{SYSTEMTAG}))"),
        outcome={'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(0, 0.2, 1.0)),
    "UACME52":
    VulnerabilityInfo(
        description="UACME UAC bypass #52",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/hfiref0x/UACME",
        precondition=Precondition(f"Windows&(Win10|Win7)&(~({ADMINTAG}|{SYSTEMTAG}))"),
        outcome={'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(0, 0.2, 1.0)),
    "UACME55":
    VulnerabilityInfo(
        description="UACME UAC bypass #55",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/hfiref0x/UACME",
        precondition=Precondition(f"Windows&(Win10|Win7)&(~({ADMINTAG}|{SYSTEMTAG}))"),
        outcome={'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(0, 0.2, 1.0)),
    "UACME61":
    VulnerabilityInfo(
        description="UACME UAC bypass #61",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/hfiref0x/UACME",
        precondition=Precondition(f"Windows&Win10&(~({ADMINTAG}|{SYSTEMTAG}))"),
        outcome={'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(0, 0.2, 1.0)),
    "MimikatzLogonpasswords":
    VulnerabilityInfo(
        description="Mimikatz sekurlsa::logonpasswords.",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/gentilkiwi/mimikatz",
        precondition=Precondition(f"Windows&({ADMINTAG}|{SYSTEMTAG})"),
        outcome={'LeakedCredentials': LeakedCredentials([])},
        rates=Rates(0, 1.0, 1.0)),
    "MimikatzKerberosExport":
    VulnerabilityInfo(
        description="Mimikatz Kerberos::list /export."
                    "Exports .kirbi files to be used with pass the ticket",
        type=VulnerabilityType.LOCAL,
        URL="https://github.com/gentilkiwi/mimikatz",
        precondition=Precondition(f"Windows&DomainJoined&({ADMINTAG}|{SYSTEMTAG})"),
        outcome={'LeakedCredentials': LeakedCredentials([])},
        rates=Rates(0, 1.0, 1.0)),
    "PassTheTicket":
    VulnerabilityInfo(
        description="Mimikatz Kerberos::ptt /export."
                    "Exports .kirbi files to be used with pass the ticket",
        type=VulnerabilityType.REMOTE,
        URL="https://github.com/gentilkiwi/mimikatz",
        precondition=Precondition(f"Windows&DomainJoined&KerberosTicketsDumped"
                                  f"&({ADMINTAG}|{SYSTEMTAG})"),
        outcome={'LeakedCredentials': LeakedCredentials([])},
        rates=Rates(0, 1.0, 1.0)),
    "RDPBF":
    VulnerabilityInfo(
        description="RDP Brute Force",
        type=VulnerabilityType.REMOTE,
        URL="https://attack.mitre.org/techniques/T1110/",
        precondition=Precondition("Windows&PortRDPOpen"),
        outcome={'LateralMove': lateralMove()},
        rates=Rates(0, 0.2, 1.0)),

    "SMBBF":
    VulnerabilityInfo(
        description="SSH Brute Force",
        type=VulnerabilityType.REMOTE,
        URL="https://attack.mitre.org/techniques/T1110/",
        precondition=Precondition("(Windows|Linux)&PortSMBOpen"),
        outcome={'LateralMove': lateralMove()},
        rates=Rates(0, 0.2, 1.0))
}

potential_linux_vulns = {
    "SudoCaching": VulnerabilityInfo(
        description="Escalating privileges from poorly configured sudo on linux/unix machines",
        type=VulnerabilityType.REMOTE,
        URL="https://attack.mitre.org/techniques/T1206/",
        precondition=Precondition(f"Linux&(~{ADMINTAG})"),
        outcome={
            'PrivilegeEsclation': PrivilegeLevel.Admin},
        rates=Rates(
            0,
            1.0,
            1.0)),
    "SSHBF": VulnerabilityInfo(
        description="SSH Brute Force",
        type=VulnerabilityType.REMOTE,
        URL="https://attack.mitre.org/techniques/T1110/",
        precondition=Precondition("Linux&PortSSHOpen"),
        outcome={
            'LateralMove': lateralMove()},
        rates=Rates(
            0,
            0.2,
            1.0)),
    "SMBBF": VulnerabilityInfo(
        description="SSH Brute Force",
        type=VulnerabilityType.REMOTE,
        URL="https://attack.mitre.org/techniques/T1110/",
        precondition=Precondition("(Windows|Linux)&PortSMBOpen"),
        outcome={
            'LateralMove': lateralMove()},
        rates=Rates(
            0,
            0.2,
            1.0))}

# These are potential endpoints that can be open in a game. Note to add any more endpoints simply
# add the protocol name to this list.
# further note that ports are stored in a tuple. This is because some protoocls
# (like SMB) have multiple official ports.
potential_ports = ["RDP", "SSH", "HTTP", "HTTPs",
                   "SMB", "SQL", "FTP", "WMI"]

# These two lists are potential node states. They are split into linux states and windows
#  states so that we can generate real graphs that aren't just totally random.
potential_linux_node_property = ["Linux", "PortRDPOpen",
                                 "PortHTTPOpen", "PortHTTPsOpen",
                                 "PortSSHOpen", "PortSMBOpen",
                                 "PortFTPOpen", "DomainJoined"]
potential_windows_node_property = ["Windows", "Win10", "PortRDPOpen",
                                   "PortHTTPOpen", "PortHTTPsOpen",
                                   "PortSSHOpen", "PortSMBOpen",
                                   "PortFTPOpen", "BITSEnabled",
                                   "Win7", "DomainJoined"]

ENV_IDENTIFIERS = Identifiers(
    ports=potential_ports,
    properties=potential_linux_node_property + potential_windows_node_property,
    local_vulnerabilities=list(potential_windows_vulns.keys()),
    remote_vulnerabilities=list(potential_windows_vulns.keys())
)


def get_properties_from_vulnerabilities(os_type, vulns):
    """Return properties provinding vulnerabilities."""
    kept_properties = set()

    if os_type == 'Windows':
        properties = potential_windows_node_property

    elif os_type == 'Linux':
        properties = potential_linux_node_property

    for p in properties:

        for _, vuln in vulns.items():
            if re.search(p, str(vuln.precondition.expression)):
                kept_properties.add(p)

    return list(kept_properties)


def select_random_vulnerablities(os_type, num_vuls):
    """Select wished vulnerabilitu number randomly among proving os type."""
    assert num_vuls >= 1 and os_type in ["Windows", "Linux"]

    if os_type == "Windows":
        keys = random.sample(potential_windows_vulns.keys(), num_vuls)
        vulns = {k: potential_windows_vulns[k] for k in keys}

    elif os_type == "Linux":
        keys = random.sample(potential_linux_vulns.keys(), num_vuls)
        vulns = {k: potential_linux_vulns[k] for k in keys}

    return vulns


def create_firewall_rules(allowing_port):
    """Return a firewall configuration."""
    firewall_config = FirewallConfiguration()
    firewall_config.incoming.clear()
    firewall_config.outgoing.clear()

    for protocol in potential_ports:
        if protocol in allowing_port:
            firewall_config.incoming.append(
                FirewallRule(protocol, RulePermission.ALLOW))
            firewall_config.outgoing.append(
                FirewallRule(protocol, RulePermission.ALLOW))

        else:
            firewall_config.incoming.append(
                FirewallRule(protocol, RulePermission.BLOCK))
            firewall_config.outgoing.append(
                FirewallRule(protocol, RulePermission.BLOCK))

    return firewall_config


def create_random_node(os_type, allowing_port):
    """Create a random node."""
    assert len(allowing_port) > 0 and os_type in ["Windows", "Linux"]

    if os_type == 'Linux':
        vulnerabilities = select_random_vulnerablities(
            os_type, random.randint(1, len(potential_linux_vulns)))

    elif os_type == 'Windows':
        vulnerabilities = select_random_vulnerablities(
            os_type, random.randint(1, len(potential_windows_vulns)))

    firewall_config = create_firewall_rules(allowing_port)
    properties = get_properties_from_vulnerabilities(os_type, vulnerabilities)

    return Node(services=[ListeningService(name=p) for p in allowing_port],
                vulnerabilities=vulnerabilities,
                properties=properties,
                firewall=firewall_config,
                value=int(random.random()),
                privilege_level=PrivilegeLevel.NoAcces)


def create_random_environment(name, size):
    """Return the generated randomly environment."""
    assert len(name) > 0 and size >= 1

    graph = nx.DiGraph()
    nodes = {}
    vuln_lib = {**potential_linux_vulns, **potential_windows_vulns}
    os_types = ["Windows", "Linux"]

    for i in range(size):
        os_type = os_types[random.randint(0, 1)]
        nodes[str(i)] = create_random_node(os_type, potential_ports)

    nodes['0'].agent_installed = True

    graph.add_nodes_from([(k, {'data': v}) for (k, v) in list(nodes.items())])

    return Environment(
        network=graph,
        identifiers=ENV_IDENTIFIERS,
        vulnerability_library=vuln_lib)


def register(id, identifiers, **kwargs):
    """Register it."""
    if id in registry.env_specs:
        ValueError('Cannot re-register id: {}'.format(id))

    spec = EnvSpec(id, **kwargs)
    spec.ports = identifiers.ports
    spec.properties = identifiers.properties
    spec.local_vulnerabilities = identifiers.local_vulnerabilities
    spec.remote_vulnerabilities = identifiers.remote_vulnerabilities

    registry.env_specs[id] = spec
