"""Provide functions and objects wich are the the basic parts of the cyber environment."""

from enum import Enum, IntEnum
from time import time
from datetime import datetime
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import boolean
from collections import OrderedDict
from typing import List

from gym import spaces
from gym.utils import seeding

ALGEBRA = boolean.BooleanAlgebra()


class Attacker:
    """Attacker goals."""

    def __init__(self,
                 reward=0.0,
                 low_availability=0.0,
                 own_atleast=0,
                 own_atleast_percent=0.0,
                 capture_flag=0
                 ):
        """Init the attacker goals. If all of them are reached, the attacker wins."""
        self.reward = reward
        self.low_availability = low_availability
        self.own_atleast = own_atleast
        self.own_atleast_percent = own_atleast_percent
        self.capture_flag = capture_flag


class CachedCredential:
    """Can appears as an action's outcome."""

    def __init__(self, node, port, credential):
        """Init the node and the port where it is possible to connect itself using the credential."""
        self.node = node
        self.port = port
        self.credential = credential


class CustomerData:
    """Correspond to many object, dataset, file..."""

    def __init__(self):
        """Init but for now we aren't using it in simulations."""
        None


class Defender:
    """Defender goals."""

    def __init__(self,
                 maintain_sla=0.0,
                 eviction=True,
                 ):
        """Init the defender goals. If all of them are reached, the attacker wins."""
        self.eviction = eviction
        self.maintain_sla = maintain_sla


class DiscriminatedUnion(spaces.Dict):
    """
    A discriminated union of simpler spaces.

    Example usage:
    self.observation_space = discriminatedunion.DiscriminatedUnion(
        {"foo": spaces.Discrete(2), "Bar": spaces.Discrete(3)})
    """

    def __init__(self,
                 spaces=None,
                 **spaces_kwargs):
        """Create a discriminated union space."""
        if spaces is None:
            super().__init__(spaces_kwargs)
        else:
            super().__init__(spaces=spaces)

    def seed(self, seed=None):
        """Return an entropy."""
        self._np_random, seed = seeding.np_random(seed)
        super().seed(seed)

    def sample(self):
        """Return an achievement with respect to the space distribution."""
        space_count = len(self.spaces.items())
        index_k = self.np_random.randint(space_count)
        kth_key, kth_space = list(self.spaces.items())[index_k]
        return OrderedDict([(kth_key, kth_space.sample())])

    def contains(self, candidate):
        """Return if a feature belongs to the space dict."""
        if not isinstance(candidate, dict) or len(candidate) != 1:
            return False
        k, space = list(candidate)[0]
        return k in self.spaces.keys()

    @classmethod
    def is_of_kind(cls, key, sample_n):
        """Return true if a given sample is of the specified discriminated kind."""
        return key in sample_n.keys()

    @classmethod
    def kind(cls, sample_n):
        """Return the discriminated kind of a given sample."""
        keys = sample_n.keys()
        assert len(keys) == 1
        return list(keys)[0]

    def __getitem__(self, key):
        """Return item associated to the passing key."""
        return self.spaces[key]

    def __repr__(self):
        """Return names."""
        return self.__class__.__name__ + \
            "(" + ", ". join([str(k) + ":" + str(s)
                              for k, s in self.spaces.items()]) + ")"

    def to_jsonable(self, sample_n):
        """Convert to json format."""
        return super().to_jsonable(sample_n)

    def from_jsonable(self, sample_n):
        """Get dict space from a jsonable sample."""
        ret = super().from_jsonable(sample_n)
        assert len(ret) == 1
        return ret

    def __eq__(self, other):
        """Check if an other DiscriminatedUnion instance is the same or not."""
        return isinstance(
            other, DiscriminatedUnion) and self.spaces == other.spaces


class EdgeAnnotation(float, Enum):
    """Define the weights in the discovered network.

    Notice that we will have to enhance this weights because of using a GNN.
    """

    KNOWS = 0.1
    REMOTE_EXPLOIT = 0.4
    LATERAL_MOVE = 0.6


class EnvironmentBounds:
    """Bounds of the environment."""

    def __init__(self,
                 maximum_total_credentials,
                 maximum_node_count,
                 maximum_discoverable_credentials_per_action,
                 port_count,
                 property_count,
                 local_attacks_count,
                 remote_attacks_count,
                 ):
        """Init bounds."""
        self.maximum_total_credentials = maximum_total_credentials
        self.maximum_node_count = maximum_node_count
        self.maximum_discoverable_credentials_per_action = maximum_discoverable_credentials_per_action
        self.port_count = port_count
        self.property_count = property_count
        self.local_attacks_count = local_attacks_count
        self.remote_attacks_count = remote_attacks_count

    @classmethod
    def of_identifiers(cls,
                       identifiers,
                       maximum_total_credentials,
                       maximum_node_count,
                       maximum_discoverable_credentials_per_action=None
                       ):
        """Can instance an EnvironmentBounds instance providing identifiers."""
        if not maximum_discoverable_credentials_per_action:
            maximum_discoverable_credentials_per_action = maximum_total_credentials

        return EnvironmentBounds(
            maximum_total_credentials=maximum_total_credentials,
            maximum_node_count=maximum_node_count,
            maximum_discoverable_credentials_per_action=maximum_discoverable_credentials_per_action,
            port_count=len(
                identifiers.ports),
            property_count=len(
                identifiers.properties),
            local_attacks_count=len(
                identifiers.local_vulnerabilities),
            remote_attacks_count=len(
                identifiers.remote_vulnerabilities))


class Environment:
    """Cyber environment."""

    def __init__(self,
                 vulnerability_library,
                 identifiers,
                 network,
                 creationTime=datetime.utcnow(),
                 lastModified=datetime.utcnow()
                 ):
        """Init creation and last modified datetime.

        network is a networkx object, vulnerability library will
        define the number of possible actions and identifiers the environment bounds.
        """
        self.network = network
        self.vulnerability_library = vulnerability_library
        self.identifiers = identifiers
        self.creationTime = creationTime
        self.lastModified = lastModified

    def nodes(self):
        """Return nodes and their data in the whole network."""
        for nodeid, nodevalue in self.network.nodes.items():
            node_data = nodevalue['data']
            yield nodeid, node_data

    def get_node(self, node_id):
        """Get data of a particular node."""
        return self.network.nodes[node_id]['data']

    def plot_environment_graph(self, path=''):
        """Get a display of the environment."""
        nx.draw(self.network,
                with_labels=True,
                node_color=[
                    n['data'].value for i,
                    n in self.network.nodes.items()],
                cmap=plt.cm.Oranges
                )
        if path:
            plt.savefig(path, format="PNG")


class ExploitFailed:
    """It is used for actions destinated to be failed."""

    def __init__(self):
        """Init."""
        None


class FirewallRule:
    """Firewall object for a specific traffic."""

    def __init__(self, port, permission, reason=''):
        """Init the rule on a specified port."""
        self.port = port
        self.permission = permission
        self.reason = reason


class Identifiers:
    """It is the environment summary."""

    def __init__(self,
                 properties=[],
                 ports=[],
                 local_vulnerabilities=[],
                 remote_vulnerabilities=[]
                 ):
        """Init."""
        self.properties = properties
        self.ports = ports
        self.local_vulnerabilities = local_vulnerabilities
        self.remote_vulnerabilities = remote_vulnerabilities

    def display(self):
        """Display it."""
        print('Properties : {}\nPorts : {}\nlocal_vulnerabilities : {}\nremote_vulnerabilities : {}\n'.format(
            self.properties, self.ports, self.local_vulnerabilities, self.remote_vulnerabilities))

        print('total properties : {}\ntotal ports : {}\ntotal local_vulnerabilities : {}\ntotal remote_vulnerability : {}\n'.format(
            len(self.properties), len(self.ports), len(self.local_vulnerabilities), len(self.remote_vulnerabilities)))


class lateralMove:
    """The most valuable outcome.

    If succesfull, it allow the agent to connect to a machine without to be present in the source node.
    """

    def __init__(self):
        """Init if the lateralMove was succesfull or not."""
        self.success = False


class LeakedCredentials:
    """Action outcome."""

    def __init__(self, credentials):
        """Init a list of CachedCredential."""
        self.credentials = credentials


class LeakedNodesId:
    """Action outcome."""

    def __init__(self, nodes):
        """Init a list of node ids."""
        self.nodes = nodes


class ListeningService:
    """Service running in a machine."""

    def __init__(self, name, allowedCredentials=[],
                 running=True, sla_weight=1.0):
        """Init it with a list of allowed credentials to have the access."""
        self.name = name
        self.allowedCredentials = allowedCredentials
        self.running = running
        self.sla_weight = sla_weight


class MachineStatus(IntEnum):
    """Return the machine status."""

    STOPPED = 0
    RUNING = 1
    IMAGING = 2


class NodeTrackingInformation:
    """This class allow us to have a local memory on what happens at a specific node.

    Furthermore, it allow us to check if an attack is repeat on a node.
    """

    def __init__(self):
        """Init with empty discovered properties and attacks.

        last connection parameter will be update once a succesfull attack is attempted.
        """
        self.last_attack = {}
        self.last_connection = None
        self.discovered_properties = set()
        self.successfull_attack = 0
        self.failed_attack = 0


class Observation:
    """This class will be usefull to encode features for the agent."""

    def __init__(self,
                 newly_discovered_nodes_count,
                 lateral_move,
                 customer_data_found,
                 probe_result,
                 escalation,
                 leaked_credentials,
                 action_mask,
                 credential_cache_length,
                 discovered_node_count,
                 discovered_nodes_properties,
                 nodes_privilegelevel,
                 credentials_cache_matrix,
                 credential_cache,
                 discovered_nodes,
                 explored_network
                 ):
        """Init parameters to build observable environment."""
        self.newly_discovered_nodes_count = newly_discovered_nodes_count
        self.lateral_move = lateral_move
        self.customer_data_found = customer_data_found
        self.probe_result = probe_result
        self.escalation = escalation
        self.leaked_credentials = leaked_credentials
        self.action_mask = action_mask
        self.credential_cache_length = credential_cache_length
        self.discovered_node_count = discovered_node_count
        self.discovered_nodes_properties = discovered_nodes_properties
        self.nodes_privilegelevel = nodes_privilegelevel
        self.credentials_cache_matrix = credentials_cache_matrix
        self.credential_cache = credential_cache
        self.discovered_nodes = discovered_nodes
        self.explored_network = explored_network


class Penalty(IntEnum):
    """Theses rewards must reflected the gravity of a failed action."""

    SUSPICIOUSNESS = -5
    SCANNING_UNOPEN_PORT = -10
    REPEAT = -1
    FAILED_LOCAL_EXPLOIT = -20
    FAILED_REMOTE_EXPLOIT = -50
    MACHINE_NOT_RUNNING = -1
    WRONG_PASSWORD = -10
    BLOCKED_BY_LOCAL_FIREWALL = -10
    BLOCKED_BY_REMOTE_FIREWALL = -10
    REPEAT_MISTAKE = -1
    DECOY_OR_HONEYPOT_TOUCHED = -100
    EXPLOIT_USE = -1
    HONEYPOT_CONTROL = 0
    USED_HONEYTOKEN = -10


class Precondition:
    """This class will be usefull to check if an agent can execute an action.

    For instance, to execute this vulnerability : https://github.com/hfiref0x/UACME,
    The agent have to be on a windows 7 or 10 machine with at least an admin tag.
    """

    def __init__(self, expr):
        """Init the condition."""
        if isinstance(expr, boolean.Expression):
            self.expression = expr
        else:
            self.expression = ALGEBRA.parse(expr)


class PrivilegeEscalation:
    """track the privilege of the agent on a node."""

    def __init__(self, level):
        """Init the privilege level."""
        self.level = level

    def tag(self):
        """Return the privilege tag."""
        return self.level


class PrivilegeLevel(IntEnum):
    """Different type of privilege level."""

    NoAcces = 0
    LocalUser = 1
    Admin = 2
    System = 3
    MAXIMUM = 3


class ProbeSucceeded:
    """Outcome that brings to the agent a list of discovered properties."""

    def __init__(self, discovered_properties):
        """Init discovered properties list."""
        self.discovered_properties = discovered_properties


class ProbeFailed:
    """Failed Probe."""

    def __init__(self):
        """Init."""
        None


class Rates:
    """Allow us to modelise an action based on a random environment error."""

    def __init__(self,
                 probingDetectionRate=0.0,
                 exploitDetectionRate=0.0,
                 successRate=1.0
                 ):
        """Init probabilities."""
        self.probingDetectionRate = probingDetectionRate
        self.exploitDetectionRate = exploitDetectionRate
        self.successRate = successRate


class Reimaging(IntEnum):
    """Number of iteration to spend to complete the reimaging."""

    REIMAGING_DURATION = 15


class Reward(IntEnum):
    """Rewards type.

    Notice that we strongly support agent to be connect as much as possible.
    In the case of the presence of decoy machines, it will be a
    strong deceptive reward.
    """

    NEW_SUCCESSFUL_ATTACK = 7
    NODE_DISCOVERED = 5
    CREDENTIAL_DISCOVERED = 3
    PROPERTY_DISCOVERED = 2
    #NODE_CONNEXION = 100
    SUCCESSFUL_EXPLOIT = 50


class RulePermission(IntEnum):
    """permission rule for a firewall."""

    ALLOW = 0
    BLOCK = 1


class FirewallConfiguration:
    """Defin list of incoming and outgoing firewall rules."""

    def __init__(self, incoming=[
        FirewallRule("RDP", RulePermission.ALLOW),
        FirewallRule("SSH", RulePermission.ALLOW),
        FirewallRule("HTTPS", RulePermission.ALLOW),
        FirewallRule("HTTP", RulePermission.ALLOW)],
        outgoing=[
        FirewallRule("RDP", RulePermission.ALLOW),
        FirewallRule("SSH", RulePermission.ALLOW),
        FirewallRule("HTTPS", RulePermission.ALLOW),
        FirewallRule("HTTP", RulePermission.ALLOW)],
    ):
        """Init both list."""
        self.outgoing = outgoing
        self.incoming = incoming


class Node:
    """Machine representation."""

    def __init__(self,
                 services=[],
                 vulnerabilities=dict(),
                 properties=[],
                 firewall=FirewallConfiguration(),
                 privilege_level=PrivilegeLevel.NoAcces,
                 value=0,
                 agent_installed=False,
                 reimagable=True,
                 last_reimaging=0.0,
                 owned_string="",
                 status=MachineStatus.RUNING,
                 sla_weight=1.0,
                 decoy_machine=False,
                 honeypot_machine=False
                 ):
        """Init parameters."""
        self.services = services
        self.vulnerabilities = vulnerabilities
        self.properties = properties
        self.firewall = firewall
        self.privilege_level = privilege_level
        self.value = value
        self.agent_installed = agent_installed
        self.reimagable = reimagable
        self.last_reimaging = last_reimaging
        self.owned_string = owned_string
        self.status = status
        self.sla_weight = sla_weight
        self.decoy_machine = decoy_machine
        self.honeypot_machine = honeypot_machine

        if agent_installed:
            self.privilege_level = PrivilegeLevel.LocalUser


class VulnerabilityType(IntEnum):
    """Can quickly inform the type of a vulnerability."""

    LOCAL = 1
    REMOTE = 2


class VulnerabilityInfo:
    """Vulnerability representation."""

    def __init__(self,
                 outcome,
                 type,
                 rates=Rates(),
                 URL="",
                 cost=1.0,
                 reward_string="",
                 precondition=Precondition('True'),
                 description=''
                 ):
        """Init parameters."""
        self.description = description
        self.type = type
        self.outcome = outcome
        self.precondition = precondition
        self.URL = URL
        self.rates = rates
        self.cost = cost
        self.reward_string = reward_string


def get_hashable_action(gym_action):
    """Return the hashable gym action."""
    action_type = list(gym_action.keys())[0]

    return tuple(list(gym_action[action_type]))


def collect_ports_from_environment(env):
    """Return the passing environment ports."""
    return collect_ports_from_nodes(
        iterate_network_nodes(env), env.vulnerability_library)


def collect_ports_from_nodes(nodes, vulnerability_library):
    """Return ports from a passing list of nodes providing a vulnerability library."""
    from_vulnerabilty_library = set()
    from_nodes_vulnerabilities = set()
    from_nodes_services = set()

    for _, v in vulnerability_library.items():
        for port in collect_ports_from_vuln(v):
            from_vulnerabilty_library.add(port)

    for _, node_info in nodes.items():
        for _, v in node_info.vulnerabilities.items():
            for port in collect_ports_from_vuln(v):
                from_nodes_vulnerabilities.add(port)

        for service in node_info.services:
            from_nodes_services.add(service.name)

    return sorted(list(from_vulnerabilty_library.union(
        from_nodes_vulnerabilities).union(from_nodes_services)))


def collect_ports_from_vuln(vulnerability):
    """Return discoverable ports in the passing vulnerablity."""
    if isinstance(vulnerability.outcome, LeakedCredentials):
        return [c.port for c in vulnerability.outcome.credentials]

    else:
        return []


def collect_properties_from_nodes(nodes):
    """Return properties from the passing list of nodes."""
    properties = set()

    for _, node_info in nodes.items():
        for p in node_info.properties:
            properties.add(p)

    return sorted(list(properties))


def collect_vulnerability_ids_from_nodes_bytype(
        nodes, global_vulnerabilities, type):
    """Return vulnerability ids with a specific type from a list of nodes providing the list of vulnerabilities."""
    vuln = set()
    for _, node_info in nodes.items():
        for id, v in node_info.vulnerabilities.items():
            if v.type == type:
                vuln.add(id)

    for id, v in global_vulnerabilities.items():
        if v.type == type:
            vuln.add(id)

    return sorted(list(vuln))


def create_network(nodes):
    """Return a networkx graph passing a list of nodes.

    Notice weights are empty.
    """
    graph = nx.DiGraph()
    graph.add_nodes_from([(k, {'data': v}) for (k, v) in list(nodes.items())])

    return graph


def escalate(current_level, escalation_level):
    """Return the new privilege level."""
    return PrivilegeLevel(max(int(current_level), int(escalation_level)))


def iterate_network_nodes(env):
    """Return a dictionnary of the network of the passing environmet."""
    nodes_data = env.network.nodes.data()
    nodes = dict()

    for node in nodes_data:
        nodes[node[0]] = node[1]['data']

    return nodes


def infer_constants_from_nodes(nodes, global_vulnerabilities):
    """Return identifiers object passing nodes and global_vulnerabilities."""
    return Identifiers(
        properties=collect_properties_from_nodes(nodes),
        ports=collect_ports_from_nodes(nodes, global_vulnerabilities),
        local_vulnerabilities=collect_vulnerability_ids_from_nodes_bytype(
            nodes, global_vulnerabilities, VulnerabilityType.LOCAL),
        remote_vulnerabilities=collect_vulnerability_ids_from_nodes_bytype(
            nodes, global_vulnerabilities, VulnerabilityType.REMOTE)
    )


def random_argmax(array):
    """Return the max of an array.

    If there are several max, we choose randomly an
    index associated with its value among these max.
    """
    max_value = np.max(array)
    max_index = np.where(array == max_value)[0]

    if max_index.shape[0] > 1:
        max_index = int(np.random.choice(max_index, size=1))
    else:
        max_index = int(max_index)

    return max_value, max_index


def random_argtop_percentile(array, percentile):
    """Return the random max of an array with respect to the passing percentile."""
    top_percentile = np.percentile(array, percentile)
    indices = np.where(array >= top_percentile)[0]

    if indices.shape[0] == 0:
        return random_argmax(array)
    elif indices.shape[0] > 1:
        max_index = int(np.random.choice(indices, size=1))
    else:
        max_index = int(indices)

    return top_percentile, max_index


def sourcenode_of_action(a):
    """Return the source node of a gym action."""
    if 'local_vulnerability' in a:

        return a['local_vulnerability'][0]

    elif 'remote_vulnerability' in a:

        return a['remote_vulnerability'][0]

    assert 'connect' in a

    return a['connect'][0]


def node_of_action(a):
    """Return the action node with respect to the GNN learner choice of a gym action."""
    if 'local_vulnerability' in a:

        return a['local_vulnerability'][0]

    elif 'remote_vulnerability' in a:

        return a['remote_vulnerability'][1]

    assert 'connect' in a

    return a['connect'][1]


def get_adjacent_matrix(observation):
    """Return the adjacent matrix providing the current observation."""
    network = observation.explored_network
    n = observation.discovered_node_count
    adjacent_matrix = np.zeros((n, n))

    for edge in network.edges.data():
        i = observation.discovered_nodes.index(edge[0])
        j = observation.discovered_nodes.index(edge[1])
        data = edge[2]
        adjacent_matrix[i, j] = data['kind_as_float']

    return adjacent_matrix
