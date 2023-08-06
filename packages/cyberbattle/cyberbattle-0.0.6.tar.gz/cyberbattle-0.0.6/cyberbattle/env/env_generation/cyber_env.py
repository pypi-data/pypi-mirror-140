"""Provide a gym environment for the cyber battle."""

import gym
from gym import spaces

import copy
import numpy as np
import random

from ...utils.objects_and_global_functions import *
from .actions import AgentActions, DefenderAgentActions

from .Iterative_defender import ScanAndReimageCompromiseMachines


class CyberBattleEnv(gym.Env):
    """The core class."""

    def __init__(self,
                 initial_environment,
                 maximum_total_credentials=1000,
                 maximum_node_count=1000,
                 maximum_discoverable_credentials_per_action=5,
                 defender_agent=ScanAndReimageCompromiseMachines(0.8, 4, 8),
                 attacker=Attacker(),
                 defender=Defender(maintain_sla=0.0, eviction=True),
                 winning_reward=5000.0,
                 losing_reward=0.0,
                 name='CyberBattleEnv',
                 positive_rewards=True
                 ):
        """Set hyper parameters, check if the initial environment is valid and reset it.

        environment               - The CyberBattle network simulation environment
        maximum_total_credentials - Maximum total number of credentials used in a network
        maximum_node_count        - Largest possible size of the network
        maximum_discoverable_credentials_per_action - Maximum number of credentials returned by a given action
        attacker_goal             - Target goal for the attacker to win and stop the simulation.
        defender_goal             - Target goal for the defender to win and stop the simulation.
        defender_constraint       - Constraint to be maintain by the defender to keep the simulation running.
        winning_reward            - Reward granted to the attacker if the simulation ends because the attacker's goal is reached.
        losing_reward             - Reward granted to the attacker if the simulation ends because the Defender's goal is reached.
        """
        self.__initial_environment = initial_environment
        self.__bounds = EnvironmentBounds.of_identifiers(
            maximum_total_credentials=maximum_total_credentials,
            maximum_node_count=maximum_node_count,
            maximum_discoverable_credentials_per_action=maximum_discoverable_credentials_per_action,
            identifiers=initial_environment.identifiers)

        self.__positive_rewards = positive_rewards
        self.__attacker = attacker
        self.__defender = defender
        self.__WINNING_REWARD = winning_reward
        self.__LOSING_REWARD = losing_reward

        self.__defender_agent = defender_agent

        self.__node_count = len(
            self.__initial_environment.network.nodes.items())

        self.__reset_environment()

        local_vulnerabilities_count = self.__bounds.local_attacks_count
        remote_vulnerabilities_count = self.__bounds.remote_attacks_count
        maximum_node_count = self.__bounds.maximum_node_count
        property_count = self.__bounds.property_count
        port_count = self.__bounds.port_count
        maximum_total_credentials = self.__bounds.maximum_total_credentials
        maximum_discoverable_credentials_per_action = self.__bounds.maximum_discoverable_credentials_per_action

        action_spaces = {
            "local_vulnerability": spaces.MultiDiscrete(
                [maximum_node_count, local_vulnerabilities_count]),
            "remote_vulnerability": spaces.MultiDiscrete(
                [maximum_node_count, maximum_node_count, remote_vulnerabilities_count]),
            "connect": spaces.MultiDiscrete(
                [maximum_node_count, maximum_node_count, port_count, maximum_total_credentials])
        }

        self.action_space = DiscriminatedUnion(action_spaces)

        action_mask_spaces = {
            "local_vulnerability":
                spaces.MultiBinary(
                    maximum_node_count *
                    local_vulnerabilities_count),
            "remote_vulnerability":
                spaces.MultiBinary(
                    maximum_node_count *
                    maximum_node_count *
                    remote_vulnerabilities_count),
            "connect":
                spaces.MultiBinary(
                    maximum_node_count *
                    maximum_node_count *
                    port_count *
                    maximum_total_credentials)
        }

        self.observation_space = spaces.Dict({
            "newly_discovered_nodescount": spaces.Discrete(maximum_node_count + 1),
            "lateral_move": spaces.Discrete(2),
            "customer_data_found": spaces.MultiBinary(2),
            "prob_result": spaces.Discrete(3),
            "escalation": spaces.MultiDiscrete(PrivilegeLevel.MAXIMUM + 1),
            "leaked_credentials": spaces.Tuple([spaces.MultiDiscrete([1 + 1, maximum_total_credentials,
                                                                      maximum_node_count, port_count]
                                                                     )] * maximum_discoverable_credentials_per_action),
            "action_mask": spaces.Dict(action_mask_spaces),
            "credential_cache_length": spaces.Discrete(maximum_node_count),
            "discovered_node_count": spaces.Discrete(maximum_node_count),
            "discovered_nodes_properties": spaces.MultiDiscrete([3] * maximum_node_count * property_count),
            "nodes_privilegelevel": spaces.MultiDiscrete([PrivilegeLevel.MAXIMUM + 1] * maximum_node_count),
            "credentials_cache_matrix": spaces.Tuple(
                [spaces.MultiDiscrete([maximum_node_count, port_count])] * maximum_total_credentials)
        })

        self.reward_range = (-np.infty, np.infty)
        self.env_name = name

        self.validate_environment(initial_environment)

    def name(self):
        """Return environment name."""
        return self.env_name

    def identifiers(self):
        """Return environment identifiers."""
        return self.__environment.identifiers

    def bounds(self):
        """Return environment bounds."""
        return self.__bounds

    def environment(self):
        """Return environment at when it's called iteration."""
        return self.__environment

    def __reset_environment(self):
        """Reset environment."""
        self.__environment = copy.deepcopy(self.__initial_environment)
        self.__discovered_nodes = []
        self.__owned_nodes_indices_cache = None
        self.__credential_cache = []
        self.__episode_rewards = []
        self.__episode_rewards = []
        self._actuator = AgentActions(self.__environment)
        self.__defender_actuator = DefenderAgentActions(self.__environment)

        self.__stepcount = 0
        self.__start_time = time()
        self.__end = False

        for node_id, node_data in self.__environment.nodes():
            if node_data.agent_installed:
                self.__discovered_nodes.append(node_id)

    def validate_environment(self, env):
        """Check environment validity.

        More precisely, ths function check if agent bounds overestimate well the environment bounds.
        """
        assert env.identifiers.ports
        assert env.identifiers.properties
        assert env.identifiers.local_vulnerabilities
        assert env.identifiers.remote_vulnerabilities

        node_count = len(env.network.nodes.items())
        if node_count > self.__bounds.maximum_node_count:
            raise ValueError(
                'Network node count ({}) exceeds the specified limit of {}'.format(
                    node_count, self.__bounds.maximum_node_count))

        nodes = iterate_network_nodes(env)

        effective_maximum_credentials_per_action = max([
            len(vulnerability.outcome.credentials)
            for _, node_info in nodes.items()
            for _, vulnerability in node_info.vulnerabilities.items()
            if isinstance(vulnerability.outcome, LeakedCredentials)
        ])

        if effective_maximum_credentials_per_action > self.__bounds.maximum_discoverable_credentials_per_action:
            raise ValueError(
                "Some action in the environment returns {} credentials wich exceeds the maximum number of discoverable credentials {}".format(
                    effective_maximum_credentials_per_action,
                    self.__bounds.maximum_discoverable_credentials_per_action))

        referenced_ports = collect_ports_from_environment(env)
        undefined_ports = set(referenced_ports).difference(
            env.identifiers.ports)
        if undefined_ports:
            raise ValueError(
                "The network has references to undefined port names: {}".format(undefined_ports))

        referenced_properties = collect_properties_from_nodes(nodes)
        undefined_properties = set(referenced_properties).difference(
            env.identifiers.properties)
        if undefined_properties:
            raise ValueError("The network has references to undefined property names: {}".format(
                undefined_properties))

        local_vulnerabilities = collect_vulnerability_ids_from_nodes_bytype(
            nodes, env.vulnerability_library, VulnerabilityType.LOCAL)
        undefined_local_vulnerabilities = set(local_vulnerabilities).difference(
            env.identifiers.local_vulnerabilities)
        if undefined_local_vulnerabilities:
            raise ValueError("The network has references to undefined local vulenrability names: {}".format(
                undefined_local_vulnerabilities))

        remote_vulnerabilities = collect_vulnerability_ids_from_nodes_bytype(
            nodes, env.vulnerability_library, VulnerabilityType.REMOTE)
        undefined_remote_vulnerabilities = set(remote_vulnerabilities).difference(
            env.identifiers.remote_vulnerabilities)
        if undefined_remote_vulnerabilities:
            raise ValueError("The network has references to undefined remote vulnerability names: {}".format(
                undefined_remote_vulnerabilities))

    def __index_to_local_vulnerabilities(self, vulnerability_index):
        """Return a local vulnerability providing its identifier index."""
        return self.__environment.identifiers.local_vulnerabilities[vulnerability_index]

    def __index_to_remote_vulnerabilities(self, vulnerability_index):
        """Return a remote vulnerability providing its identifier index."""
        return self.__environment.identifiers.remote_vulnerabilities[vulnerability_index]

    def __index_to_portname(self, portname_index):
        """Return a portname providing its identifier index."""
        return self.__environment.identifiers.ports[portname_index]

    def __portname_to_index(self, portname):
        """Return a identifier portname index providing it."""
        return self.__environment.identifiers.ports.index(portname)

    def __internal_node_id_from_external_node_index(self, node_external_index):
        """Return the node position in the list of discovered nodes."""
        if node_external_index < 0:
            raise ValueError(
                "Node index must be positive, give {}".format(node_external_index))

        if node_external_index >= len(self.__discovered_nodes):
            raise ValueError(
                "Node index {} is not yet discovered".format(node_external_index))

        return self.__discovered_nodes[int(node_external_index)]

    def __find_external_index(self, node_id):
        """Return the node position in the discovered node."""
        return self.__discovered_nodes.index(node_id)

    def __agent_owns_node(self, node_id):
        """Return True if then agent owns the passing node and false otherwise."""
        node_info = self.__environment.get_node(node_id)
        return node_info.agent_installed

    def apply_mask(self, action, mask):
        """Check if the action is executable by the agent providing a mask determining the observable action space."""
        if mask is None:
            mask = self.compute_action_mask()

        keys = action.keys()
        assert len(keys) == 1
        field_name = list(keys)[0]
        field_mask, coordinates = mask[field_name], action[field_name]

        return int(field_mask[tuple(coordinates)]) == 1

    def __get_blank_action_mask(self):
        """Return a mask with 0 executable action."""
        node_count = self.__node_count
        local_vulnerabilities = self.__bounds.local_attacks_count
        remote_vulnerabilities = self.__bounds.remote_attacks_count
        port_count = self.__bounds.port_count

        local = np.zeros((node_count, local_vulnerabilities))
        remote = np.zeros((node_count, node_count, remote_vulnerabilities))
        connect = np.zeros(
            (node_count,
             node_count,
             port_count,
             self.__bounds.maximum_total_credentials))

        return {'local_vulnerability': local,
                'remote_vulnerability': remote, 'connect': connect}

    def __update_action_mask(self, bitmask):
        """Update executable action on the providing mask."""
        local_vulnerabilities = self.__bounds.local_attacks_count
        remote_vulnerabilities = self.__bounds.remote_attacks_count
        port_count = self.__bounds.port_count

        for source_node_id in self.__discovered_nodes:
            if self.__agent_owns_node(source_node_id):
                source_index = self.__find_external_index(source_node_id)

                for vulnerability_index in range(local_vulnerabilities):
                    vulnerability_id = self.__index_to_local_vulnerabilities(
                        vulnerability_index)
                    if vulnerability_id in self.__environment.vulnerability_library or \
                            vulnerability_id in self.__environment.get_node(source_node_id).vulnerabilities:

                        bitmask["local_vulnerability"][source_index,
                                                       vulnerability_index] = 1

                for target_node_id in self.__discovered_nodes:
                    target_index = self.__find_external_index(target_node_id)
                    bitmask["remote_vulnerability"][source_index,
                                                    target_index, :remote_vulnerabilities] = 1

                    bitmask["connect"][source_index, target_index,
                                       :port_count, :len(self.__credential_cache)] = 1

        return bitmask

    def compute_action_mask(self):
        """Return an updated mask."""
        bitmask = self.__get_blank_action_mask()
        return self.__update_action_mask(bitmask)

    def __execute_action(self, action, log):
        """Execute a gym action in the environment."""
        assert 1 == len(action.keys())

        if 'local_vulnerability' in action:
            source_node_index, vulnerability_index = action["local_vulnerability"]

            return self._actuator.exploit_local_vulnerability(
                self.__internal_node_id_from_external_node_index(
                    source_node_index),
                self.__index_to_local_vulnerabilities(vulnerability_index),
                log
            )

        elif "remote_vulnerability" in action:
            source_node_index, target_node_index, vulnerability_index = action[
                "remote_vulnerability"]

            return self._actuator.exploit_remote_vulnerability(
                self.__internal_node_id_from_external_node_index(
                    source_node_index),
                self.__internal_node_id_from_external_node_index(
                    target_node_index),
                self.__index_to_remote_vulnerabilities(vulnerability_index),
                log
            )

        elif "connect" in action:
            source_node_index, target_node_index, port_index, credential_cache_index = action[
                "connect"]

            assert credential_cache_index >= 0
            assert credential_cache_index < len(self.__credential_cache)

            source_node_id = self.__internal_node_id_from_external_node_index(
                source_node_index)
            target_node_id = self.__internal_node_id_from_external_node_index(
                target_node_index)

            return self._actuator.connect_to_remote_machine(
                source_node_id,
                target_node_id,
                self.__index_to_portname(port_index),
                self.__credential_cache[credential_cache_index].credential,
                log)

    def __get_blank_observation(self):
        """Init an observation assuming executed action didn't interfered with the environment."""
        return Observation(
            newly_discovered_nodes_count=0,
            leaked_credentials=tuple([np.array(
                [0, 0, 0, 0]) * self.__bounds.maximum_discoverable_credentials_per_action]),
            lateral_move=0,
            customer_data_found=0,
            escalation=PrivilegeLevel.NoAcces,
            action_mask=self.__get_blank_action_mask(),
            probe_result=0,
            credentials_cache_matrix=np.zeros((1, 2)),
            credential_cache_length=len(self.__credential_cache),
            discovered_node_count=len(self.__discovered_nodes),
            discovered_nodes_properties=np.zeros(
                (len(self.__discovered_nodes), self.__bounds.property_count)),
            nodes_privilegelevel=np.zeros(len(self.__discovered_nodes)),
            credential_cache=self.__credential_cache,
            discovered_nodes=self.__discovered_nodes,
            explored_network=self.__get_explored_network()
        )

    def __property_vector(self, node_id):
        """Return an array indicating each discovered properties for a discovered node."""
        properties_indices = list(
            self._actuator.get_discovered_properties(node_id))
        is_owned = self._actuator.get_node_privilegelevel(
            node_id) >= PrivilegeLevel.LocalUser

        if is_owned:
            vector = np.ones(self.__bounds.property_count, dtype=int) * -1
        else:
            vector = np.zeros(self.__bounds.property_count, dtype=int)

        vector[properties_indices] = 1
        return vector

    def __get_property_matrix(self):
        """Return an array indicating each discovered properties for each discovered nodes."""
        return np.array([self.__property_vector(node_id).tolist()
                        for node_id, _ in self._actuator.discovered_nodes()])

    def __get__owned_nodes_indices(self):
        """Return external indices of owned nodes."""
        if self.__owned_nodes_indices_cache is None:
            owned_nodes_id = self._actuator.get_nodes_with_atleast_privilegelevel(
                PrivilegeLevel.LocalUser)
            self.__owned_nodes_indices_cache = [
                self.__find_external_index(n) for n in owned_nodes_id]

        return self.__owned_nodes_indices_cache

    def __get_privilegelevel_array(self):
        """Return privilege level for each discovered nodes."""
        return np.array([int(self._actuator.get_node_privilegelevel(node_id))
                        for node_id in self.__discovered_nodes])

    def __observation_reward_from_action_result(self, outcome):
        """Build an observation preprocessing the outcome of the executed action."""
        obs = self.__get_blank_observation()

        if isinstance(outcome, LeakedNodesId):
            newly_discovered_nodes_count = 0
            for node in outcome.nodes:
                if node not in self.__discovered_nodes:
                    self.__discovered_nodes.append(node)
                    newly_discovered_nodes_count += 1

            obs.newly_discovered_nodes_count = newly_discovered_nodes_count

        elif isinstance(outcome, LeakedCredentials):
            newly_discovered_nodes_count = 0
            newly_discovered_creds = []

            for cached_credential in outcome.credentials:
                if cached_credential.node not in self.__discovered_nodes:
                    self.__discovered_nodes.append(cached_credential.node)
                    newly_discovered_nodes_count += 1

                if cached_credential not in self.__credential_cache:
                    self.__credential_cache.append(cached_credential)
                    newly_discovered_creds.append(
                        (len(self.__credential_cache) - 1, cached_credential))

                obs.newly_discovered_nodes_count = newly_discovered_nodes_count
                obs.leaked_credentials = tuple(
                    [
                        1,
                        cache_index,
                        self.__find_external_index(
                            cached_credential.node),
                        self.__portname_to_index(
                            cached_credential.port)] for cache_index,
                    cached_credential in newly_discovered_creds)

        elif isinstance(outcome, lateralMove):
            obs.lateral_move = 1
        elif isinstance(outcome, CustomerData):
            obs.customer_data_found = 1
        elif isinstance(outcome, ProbeSucceeded):
            obs.probe_result = 2
        elif isinstance(outcome, ProbeFailed):
            obs.probe_result = 1
        elif isinstance(outcome, PrivilegeEscalation):
            obs.escalation = outcome.tag()

        x = np.zeros((len(self.__credential_cache), 2))
        for cache_index, cached_credential in enumerate(
                self.__credential_cache):
            x[cache_index, :] = np.array([self.__find_external_index(
                cached_credential.node), self.__portname_to_index(cached_credential.port)])

        obs.credentials_cache_matrix = x

        obs.credential_cache_length = len(self.__credential_cache)
        obs.credential_cache = self.__credential_cache
        obs.discovered_node_count = len(self.__discovered_nodes)
        obs.discovered_nodes = self.__discovered_nodes
        obs.explored_network = self.__get_explored_network()
        obs.discovered_nodes_properties = self.__get_property_matrix()
        obs.nodes_privilegelevel = self.__get_privilegelevel_array()

        obs.action_mask = self.__update_action_mask(obs.action_mask)

        return obs

    def is_owned(self, node):
        """Return True if node is owned or False otherwise."""
        node_id = self.__internal_node_id_from_external_node_index(node)

        return self._actuator.get_node_privilegelevel(
            node_id) > PrivilegeLevel.NoAcces

    def is_action_valid(self, action, action_mask=None):
        """Check if ppassing gym action is executable with respect to the providing mask."""
        assert 1 == len(action.keys())

        kind = list(action.keys())[0]
        in_range = False
        n_discovered_nodes = len(self.__discovered_nodes)
        if kind == 'local_vulnerability':
            source_node, vulnerability_index = action['local_vulnerability']
            in_range = source_node < n_discovered_nodes and self.is_owned(
                source_node) and vulnerability_index < self.__bounds.local_attacks_count
        elif kind == 'remote_vulnerability':
            source_node, target_node, vulnerability_index = action['remote_vulnerability']
            in_range = source_node < n_discovered_nodes \
                and self.is_owned(source_node) \
                and target_node < n_discovered_nodes \
                and vulnerability_index < self.__bounds.remote_attacks_count
        elif kind == 'connect':
            source_node, target_node, port_index, credential_cache_index = action['connect']
            in_range = source_node < n_discovered_nodes \
                and self.is_owned(source_node) \
                and target_node < n_discovered_nodes \
                and port_index < self.__bounds.port_count \
                and credential_cache_index < len(self.__credential_cache)

        return in_range and self.apply_mask(action, action_mask)

    def __get_explored_network(self):
        """Return the observable network."""
        known_nodes = [
            node_id for node_id,
            _ in self._actuator.discovered_nodes()]
        network = self.__environment.network
        subgraph = nx.DiGraph()

        for node_id in known_nodes:

            subgraph.add_node(node_id)
            if 'data' in network[node_id]:
                node_info = network[node_id]['data']

                if node_info is not None:
                    if not node_info.agent_installed:
                        subgraph[node_id]['data'] = None

                    subgraph.nodes[node_id]['privilege_level'] = int(
                        self._actuator.get_node_privilegelevel(node_id))
                    subgraph.nodes[node_id]['flags'] = list(
                        self._actuator.get_discovered_properties(node_id))
                    subgraph.nodes[node_id]['flags_bits'] = self.__property_vector(
                        node_id)

        for edge in network.edges.data():
            source = edge[0]
            target = edge[1]
            data = edge[2]

            subgraph.add_edge(
                source,
                target,
                kind=data['kind'],
                kind_as_float=data['kind_as_float'])

        return subgraph

    def __attacker_goal_reached(self):
        """Check if attackers goals are reached or not."""
        goal = self.__attacker
        captured_flag = self._actuator._captured_flags

        if np.sum(self.__episode_rewards) < goal.reward:
            return False

        nodes_owned = self.__get__owned_nodes_indices()
        owned_count = len(nodes_owned)

        if owned_count < goal.own_atleast:
            return False

        if owned_count / self.__node_count < goal.own_atleast_percent:
            return False

        if self.__defender_agent is not None and \
                self.__defender_actuator.network_availability() >= goal.low_availability:
            return False

        if captured_flag != goal.capture_flag:
            return False

        return True

    def __defender_constraints_broken(self):
        """Check if defender constraints are broken or not."""
        constraint = self.__defender

        if self.__defender_agent is not None and \
                self.__defender_actuator.network_availability() < constraint.maintain_sla:
            return True

        return False

    def __defender_goal_reached(self):
        """Check if defender goals are reached or not."""
        if self.__defender.eviction:
            return len(self.__get__owned_nodes_indices()) == 0

        return False

    def step(self, action, log):
        """Execute passing action on the environment."""
        if self.__end:
            raise ValueError("new episode must be started with env.reset()")

        self.__stepcount += 1
        duration = time() - self.__start_time
        log, reward, outcome = self.__execute_action(
            action, log)
        obs = self.__observation_reward_from_action_result(outcome)

        if self.__defender_agent:
            log = self.__defender_actuator.on_attacker_step_taken(log)
            log = self.__defender_agent.step(
                self.__environment,
                self.__defender_actuator,
                self.__stepcount,
                log)

        self.__owned_nodes_indices_cache = None

        if self.__attacker_goal_reached(
        ) or self.__defender_constraints_broken():
            self.__end = True
            reward += self.__WINNING_REWARD
        elif self.__defender_goal_reached():
            self.__end = True
            reward += self.__LOSING_REWARD
        else:
            reward = max(0, reward) if self.__positive_rewards else reward

        info = {
            'description': 'CyberBattle Simulation',
            'duration in ms': duration,
            'step count': self.__stepcount,
            'network availability': self.__defender_actuator.network_availability()}

        self.__episode_rewards.append(reward)

        return log, obs, reward, self.__end, info

    def already_done(self, action):
        """Return whether the agent already performed the passing action or not."""
        return get_hashable_action(action) in self._actuator.get_done_actions()

    def reset(self):
        """Reset the environment."""
        self.__reset_environment()
        observation = self.__get_blank_observation()
        observation.action_mask = self.compute_action_mask()
        observation.discovered_nodes_properties = self.__get_property_matrix()
        observation.nodes_privilegelevel = self.__get_privilegelevel_array()
        self.__owned_nodes_indices_cache = None

        return observation

    def sample_connect_action_in_expected_range(self):
        """Return a connect gym action."""
        discovered_credential_count = len(self.__credential_cache)

        if discovered_credential_count == 0:
            raise ValueError(
                "Cannot sample a connect action until the agent discovers more potential target nodes")

        return {'connect': np.array([
            random.choice(self.__get__owned_nodes_indices()),
            random.randint(0, len(self.__discovered_nodes) - 1),
            random.randint(0, self.__bounds.port_count - 1),
            random.randint(0, discovered_credential_count - 1)
        ])}

    def sample_action_in_range(self, kinds=None):
        """Return a random gym action."""
        discovered_credential_count = len(self.__credential_cache)

        if kinds is None:
            kinds = [0, 1, 2]

        if discovered_credential_count == 0 and 2 in kinds:
            kinds.remove(2)

        assert len(kinds) != 0

        kind = random.choice(kinds)

        if kind == 2:
            action = self.sample_connect_action_in_expected_range()

        elif kind == 1:
            action = {'local_vulnerability': np.array([
                random.choice(self.__get__owned_nodes_indices()),
                random.randint(0, self.__bounds.local_attacks_count - 1)
            ])}

        elif kind == 0:
            action = {'remote_vulnerability': np.array([
                random.choice(self.__get__owned_nodes_indices()),
                random.randint(0, len(self.__discovered_nodes) - 1),
                random.randint(0, self.__bounds.remote_attacks_count - 1)
            ])}

        return action

    def sample_valid_action(self, kinds=None):
        """Return a random executable action."""
        action_mask = self.compute_action_mask()
        action = self.sample_action_in_range(kinds)
        while not self.is_action_valid(action,
                                       action_mask):
            action = self.sample_action_in_range(kinds)

        return action
