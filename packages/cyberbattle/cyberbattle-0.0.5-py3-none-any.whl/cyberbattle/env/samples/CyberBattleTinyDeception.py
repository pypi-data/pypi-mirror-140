from copy import deepcopy
import random

from ..env_generation.cyber_env import CyberBattleEnv
from ...utils.objects_and_global_functions import *

default_allow_rules = [
    FirewallRule("SSH", RulePermission.ALLOW),
]

# Network nodes involved in the Capture the flag game
nodes_tiny = {
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


def get_services(nodes):

    services = set()

    for n in nodes:

        for s in nodes[n].services:

            services.add(s.name)

    return services


def global_vulnerabilities(nodes):

    gv = dict()

    for node in nodes:

        for vulnerability in nodes[node].vulnerabilities:

            if vulnerability not in gv:

                gv[vulnerability] = nodes[node].vulnerabilities[vulnerability]

    return gv


def add_honeypot(based_nodes, nb_honeytoken, target_nodes):

    nodes = deepcopy(based_nodes)

    nb_nodes = len(nodes)
    nb_honeypot = len(target_nodes)

    assert nb_nodes > nb_honeypot

    retained_nodes = target_nodes
    retained_nodes_outcome = random.sample(list(nodes), k=nb_honeytoken)
    services = get_services(nodes)
    honeypots = dict()
    honeytoken_id = 0

    for rn, rno in zip(retained_nodes, retained_nodes_outcome):

        name = rn + '_HP'
        hp = deepcopy(nodes[rn])
        hp.honeypot_machine = True

        vulnerabilities = dict()

        for i in range(nb_honeytoken):

            if i % 2 == 0:

                v = VulnerabilityInfo(
                    outcome=LeakedCredentials(
                        credentials=[
                            CachedCredential(
                                node=rno,
                                port=random.sample(services, k=1)[0],
                                credential='hhhhc_' + str(honeytoken_id)
                            )
                        ]
                    ),
                    type=VulnerabilityType.REMOTE
                )

            else:

                v = VulnerabilityInfo(
                    outcome=LeakedNodesId(
                        nodes=['hhhhl_' + str(honeytoken_id)]
                    ),
                    type=VulnerabilityType.REMOTE
                )

            vulnerabilities['ht_' + str(honeytoken_id)] = v
            honeytoken_id += 1

        hp.vulnerabilities = vulnerabilities
        hp.services = [
            ListeningService(
                s, allowedCredentials=[name]) for s in random.sample(
                services, k=random.randint(
                    0, len(services)))]
        hp.value = 0
        node_containing_hp_cred, node_containing_hp_link = random.sample(
            list(nodes), k=2)
        nodes[node_containing_hp_cred].vulnerabilities[name + ' get cred'] = VulnerabilityInfo(
            type=VulnerabilityType.REMOTE,
            outcome=LeakedCredentials(
                credentials=[
                    CachedCredential(
                        node=name,
                        port=random.sample(services, k=1)[0],
                        credential=name
                    )
                ]
            )
        )

        nodes[node_containing_hp_link].vulnerabilities[name + ' get link'] = VulnerabilityInfo(
            type=VulnerabilityType.REMOTE, outcome=LeakedNodesId(nodes=[name]))

        honeypots[name] = hp

    return {**nodes, **honeypots}


def add_decoy(based_nodes, target_nodes):

    nodes = deepcopy(based_nodes)

    nb_nodes = len(nodes)
    nb_decoy = len(target_nodes)

    assert nb_nodes > nb_decoy

    retained_nodes = target_nodes
    retained_nodes_outcome = random.sample(list(nodes), k=2)
    services = get_services(nodes)
    Decoys = dict()

    for rn in retained_nodes:

        name = rn + '_D'
        d = deepcopy(nodes[rn])
        d.decoy_machine = True
        d.value = 0

        node_containing_hp_cred = retained_nodes_outcome[0]
        node_containing_hp_link = retained_nodes_outcome[1]
        d.services = [
            ListeningService(
                s, allowedCredentials=[name]) for s in random.sample(
                services, k=random.randint(
                    0, len(services)))]
        Decoys[name] = d
        nodes[node_containing_hp_cred].vulnerabilities[name + ' get cred'] = VulnerabilityInfo(
            type=VulnerabilityType.REMOTE,
            outcome=LeakedCredentials(
                credentials=[
                    CachedCredential(
                        node=name,
                        port=random.sample(services, k=1)[0],
                        credential=name
                    )
                ]
            )
        )

        nodes[node_containing_hp_link].vulnerabilities[name + ' get link'] = VulnerabilityInfo(
            type=VulnerabilityType.REMOTE, outcome=LeakedNodesId(nodes=[name]))

    return {**nodes, **Decoys}


def add_deceptive_elements(
        nodes,
        nb_honeytoken=0,
        hp_target_nodes=[],
        decoy_target_nodes=[]):

    env_with_hp = add_honeypot(
        nodes,
        nb_honeytoken=nb_honeytoken,
        target_nodes=hp_target_nodes)
    env_with_d = add_decoy(nodes, target_nodes=decoy_target_nodes)

    return {**env_with_hp, **env_with_d}


nb_honeytoken = 2


def new_environment_hp_website(nodes):

    nodes_env = add_deceptive_elements(
        nodes,
        nb_honeytoken=nb_honeytoken,
        hp_target_nodes=['Website'])
    global_vulnerability = global_vulnerabilities(nodes_env)

    return Environment(
        network=create_network(nodes_env),
        vulnerability_library=global_vulnerability,
        identifiers=infer_constants_from_nodes(
            nodes_env,
            global_vulnerability))


def new_environment_hp_websiteDirectory(nodes):

    nodes_env = add_deceptive_elements(
        nodes,
        nb_honeytoken=nb_honeytoken,
        hp_target_nodes=['Website.Directory'])
    global_vulnerability = global_vulnerabilities(nodes_env)

    return Environment(
        network=create_network(nodes_env),
        vulnerability_library=global_vulnerability,
        identifiers=infer_constants_from_nodes(
            nodes_env,
            global_vulnerability))


def new_environment_decoy_website(nodes):

    nodes_env = add_deceptive_elements(
        nodes,
        nb_honeytoken=nb_honeytoken,
        decoy_target_nodes=['Website'])
    global_vulnerability = global_vulnerabilities(nodes_env)

    return Environment(
        network=create_network(nodes_env),
        vulnerability_library=global_vulnerability,
        identifiers=infer_constants_from_nodes(
            nodes_env,
            global_vulnerability))


def new_environment_decoy_websiteDirectory(nodes):

    nodes_env = add_deceptive_elements(
        nodes,
        nb_honeytoken=nb_honeytoken,
        decoy_target_nodes=['Website.Directory'])
    global_vulnerability = global_vulnerabilities(nodes_env)

    return Environment(
        network=create_network(nodes_env),
        vulnerability_library=global_vulnerability,
        identifiers=infer_constants_from_nodes(
            nodes_env,
            global_vulnerability))


def new_environment_deception_env(nodes):

    nodes_env = add_deceptive_elements(
        nodes,
        nb_honeytoken=nb_honeytoken,
        decoy_target_nodes=['Website', 'Website.Directory'],
        hp_target_nodes=['Website', 'Website.Directory'])

    global_vulnerability = global_vulnerabilities(nodes_env)

    return Environment(
        network=create_network(nodes_env),
        vulnerability_library=global_vulnerability,
        identifiers=infer_constants_from_nodes(
            nodes_env,
            global_vulnerability))


def identifiers_envs(nodes):

    identifiers = dict()

    hps = [['Website'], ['Website.Directory'],
           [], [], ['Website', 'Website.Directory']]
    decoys = [[], [], ['Website'], ['Website.Directory'],
              ['Website', 'Website.Directory']]
    names = [
        'Website_honeypot',
        'Website.Directory_honeypot',
        'Website_decoy',
        'Website.Directory_decoy',
        'Deception_env'
    ]

    for hp, decoy, name in zip(hps, decoys, names):

        nodes_env = add_deceptive_elements(
            nodes,
            nb_honeytoken=nb_honeytoken,
            decoy_target_nodes=decoy,
            hp_target_nodes=hp)
        global_vulnerability = global_vulnerabilities(nodes_env)

        identifiers[name] = infer_constants_from_nodes(
            nodes_env, global_vulnerability)

    return identifiers


Tiny_deception_IDENTIFIERS = identifiers_envs(nodes_tiny)


class Tiny_env_hp_website(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(initial_environment=new_environment_hp_website(nodes_tiny), **kwargs)


class Tiny_env_hp_websiteDirectory(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(
            initial_environment=new_environment_hp_websiteDirectory(nodes_tiny),
            **kwargs)


class Tiny_env_decoy_website(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(initial_environment=new_environment_decoy_website(nodes_tiny), **kwargs)


class Tiny_env_decoy_websiteDirectory(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(
            initial_environment=new_environment_decoy_websiteDirectory(nodes_tiny),
            **kwargs)


class Tiny_deception_env(CyberBattleEnv):

    def __init__(self, **kwargs):

        super().__init__(initial_environment=new_environment_deception_env(nodes_tiny), **kwargs)
