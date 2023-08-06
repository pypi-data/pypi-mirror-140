"""This file allow us to perform an action into the environment."""

import boolean

from collections import OrderedDict
from time import time
from ...utils.objects_and_global_functions import *

import pandas as pd
import IPython.core.display as d

ALGEBRA = boolean.BooleanAlgebra()


class AgentActions:
    """Class for the environment attacker actuator."""

    def __init__(self, environment):
        """Init parameters, they will be the attacker point of view."""
        self._environment = environment
        self._gathered_credentials = set()
        self._discovered_nodes = OrderedDict()
        self._captured_flags = 0

        self.privilege_tags = [PrivilegeEscalation(
            p).tag() for p in list(PrivilegeLevel)]

        for i, node in environment.nodes():
            if node.agent_installed:
                self.__mark_node_as_owned(i, PrivilegeLevel.LocalUser)
        
        self.report_done_attacks = []

    def discovered_nodes(self):
        """Yield discovered node ids and their data."""
        for node_id in self._discovered_nodes:
            yield (node_id, self._environment.get_node(node_id))

    def _check_prerequisites(self, target, vulnerability):
        """Check if the precondition to execute the passing vulnerability on the providing target is verified."""
        node_data = self._environment.network.nodes[target]['data']
        node_flags = node_data.properties
        expr = vulnerability.precondition.expression

        true_value = ALGEBRA.parse('true')
        false_value = ALGEBRA.parse('false')
        mapping = {i: true_value if str(i) in node_flags else false_value
                   for i in expr.get_symbols()}
        is_true = expr.subs(mapping).simplify() == true_value

        return is_true

    def list_vulnerabilities_in_target(self, target, type_filter):
        """Return the vulnerabilities list with the providing type in the passing target node."""
        if not self._environment.network.has_node(target):
            return ValueError('invalid node id {}'.format(target))

        target_node_data = self._environment.get_node(target)

        global_vuln = {
            vuln_id for vuln_id,
            vulnerability in self._environment.vulnerability_library.items() if (
                type_filter is None or vulnerability.type == type_filter) and self._check_prerequisites(
                target,
                vulnerability)}

        local_vuln = {
            vuln_id for vuln_id,
            vulnerability in target_node_data.vulnerabilities.items() if (
                type_filter is None or vulnerability.type == type_filter) and self._check_prerequisites(
                target,
                vulnerability)}

        return list(global_vuln.union(local_vuln))

    def __annotate_edge(self, source_node_id, target_node_id, new_annotation):
        """Update or create an edge between providing source and target node id."""
        edge_annotation = self._environment.network.get_edge_data(
            source_node_id, target_node_id)
        if edge_annotation is not None:
            if 'kind' in edge_annotation:
                new_annotation = EdgeAnnotation(
                    max(edge_annotation['kind'].value, new_annotation.value))
            else:
                new_annotation = EdgeAnnotation(new_annotation.value)

        self._environment.network.add_edge(
            source_node_id,
            target_node_id,
            kind=new_annotation,
            kind_as_float=float(new_annotation))

    def get_discovered_properties(self, node_id):
        """Return discovered properties in passing node id."""
        return self._discovered_nodes[node_id].discovered_properties

    def __mark_node_as_discovered(self, node_id):
        """Add the node id to the discovered node list and start tracking it."""
        newly_discovered = node_id not in self._discovered_nodes
        if newly_discovered:
            self._discovered_nodes[node_id] = NodeTrackingInformation()

        return newly_discovered

    def __mark_node_properties_as_discovered(self, node_id, properties):
        """Update discovered properties in the passing node id."""
        properties_indices = [self._environment.identifiers.properties.index(
            p) for p in properties if p not in self.privilege_tags]

        if node_id in self._discovered_nodes:
            before_count = len(
                self._discovered_nodes[node_id].discovered_properties)
            self._discovered_nodes[node_id].discovered_properties = self._discovered_nodes[node_id].discovered_properties.union(
                properties_indices)
        else:
            before_count = 0
            self._discovered_nodes[node_id] = NodeTrackingInformation(
                discovered_properties=set(properties_indices))

        newly_dicovered_properties = len(
            self._discovered_nodes[node_id].discovered_properties) - before_count

        return newly_dicovered_properties

    def __mark_allnodeproperties_as_discovered(self, node_id):
        """Mark all discoverable properties in the providing nodes."""
        node_info = self._environment.network.nodes[node_id]['data']

        return self.__mark_node_properties_as_discovered(
            node_id, node_info.properties)

    def __mark_node_as_owned(
            self, node_id, privilege=PrivilegeLevel.LocalUser):
        """Mark providing node id as owned and set the privilege level with the passing privilege tag."""
        if node_id not in self._discovered_nodes:
            self._discovered_nodes[node_id] = NodeTrackingInformation()

        node_info = self._environment.get_node(node_id)
        node_info.agent_installed = True
        node_info.privilege_level = escalate(
            node_info.privilege_level, privilege)
        self._environment.network.nodes[node_id].update({'data': node_info})

        return self.__mark_allnodeproperties_as_discovered(node_id)

    def __mark_discovered_entities(self, reference_node, outcome, log):
        """Mark discovered entities providing the source and the outcome of the attack."""
        newly_discovered_nodes = 0
        newly_discovered_nodes_value = 0
        newly_discovered_credentials = 0

        if isinstance(outcome, LeakedCredentials):
            for credential in outcome.credentials:
                if self.__mark_node_as_discovered(credential.node):
                    log += 'discovered node : {}'.format(credential.node)
                    newly_discovered_nodes += 1
                    newly_discovered_nodes_value += self._environment.get_node(
                        credential.node).value

                if credential.credential not in self._gathered_credentials:
                    newly_discovered_credentials += 1
                    self._gathered_credentials.add(credential.credential)

                log += 'discovered credential : {}\n'.format(
                    credential.credential)
                self.__annotate_edge(
                    reference_node,
                    credential.node,
                    EdgeAnnotation.KNOWS)

        elif isinstance(outcome, LeakedNodesId):
            for node_id in outcome.nodes:
                if self.__mark_node_as_discovered(node_id):
                    newly_discovered_nodes += 1
                    newly_discovered_nodes_value += self._environment.get_node(
                        node_id).value

                self.__annotate_edge(
                    reference_node, node_id, EdgeAnnotation.KNOWS)

        return log, newly_discovered_nodes, newly_discovered_nodes_value, newly_discovered_credentials

    def get_node_privilegelevel(self, node_id):
        """Get the current privilige tag on the passing node id."""
        node_info = self._environment.get_node(node_id)

        return node_info.privilege_level

    def get_nodes_with_atleast_privilegelevel(self, level):
        """Select nodes where the privilege tag is higher than the providing threshold."""
        return [n for n, info in self._environment.nodes()
                if info.privilege_level >= level]

    def is_node_discovered(self, node_id):
        """Check if the passing node id is discovered."""
        return node_id in self._discovered_nodes

    def __process_outcome(self,
                          expected_type,
                          vulnerability_id,
                          node_id,
                          node_info,
                          local_or_remote,
                          failed_penality,
                          log
                          ):
        """Input is a set of informations about the attack.

        The aim here is to reveal the reward (or penalty) provided by the attack on the environment.
        """
        lookup_key = (vulnerability_id, local_or_remote)

        already_executed = lookup_key in self._discovered_nodes[node_id].last_attack

        if 'hhhhl_' in node_id:

            if already_executed:
                return log, False, Penalty.REPEAT_MISTAKE, None

            else:
                return log, False, Penalty.USED_HONEYTOKEN, None

        if node_info.decoy_machine:

            if already_executed:
                return log, False, Penalty.REPEAT_MISTAKE, None

            else:
                return log, False, Penalty.DECOY_OR_HONEYPOT_TOUCHED, None

        if node_info.status != MachineStatus.RUNING:
            log += 'Penalty : Target machine not running\n'
            return log, False, Penalty.SUSPICIOUSNESS, None

        is_inplace_vulnerability = vulnerability_id in node_info.vulnerabilities

        if is_inplace_vulnerability:
            vulnerabilities = node_info.vulnerabilities
        else:
            log += "Vulnerability '{}' not supported by node '{}\n".format(
                vulnerability_id, node_id)
            return log, False, Penalty.SUSPICIOUSNESS, None

        vulnerability = vulnerabilities[vulnerability_id]
        outcome = vulnerability.outcome

        if vulnerability.type != expected_type:
            raise ValueError(
                "vulnerability id '{}' is for an attack of type {}, expecting : {}".format(
                    vulnerability_id, vulnerability.type, expected_type))

        if not self._check_prerequisites(node_id, vulnerability):
            return log, False, failed_penality, ExploitFailed()

        reward = 0

        if isinstance(outcome, PrivilegeEscalation):
            if outcome.tag() in node_info.properties:
                return False, Penalty.REPEAT, outcome

            self.__mark_node_as_owned(node_id, outcome.level)

            node_info.properties.append(outcome.tag())

        if isinstance(outcome, ProbeSucceeded):

            for p in outcome.discovered_properties:
                assert p in node_info.properties

            newly_discovered_properties = self.__mark_node_properties_as_discovered(
                node_id, outcome.discovered_properties)

            reward += newly_discovered_properties * Reward.PROPERTY_DISCOVERED

        if node_id not in self._discovered_nodes:
            self._discovered_nodes[node_id] = NodeTrackingInformation()

        if already_executed:
            last_time = self._discovered_nodes[node_id].last_attack[lookup_key]
            if node_info.last_reimaging is None or last_time >= node_info.last_reimaging:
                reward += Penalty.REPEAT

        else:
            reward += Reward.NEW_SUCCESSFUL_ATTACK

        self._discovered_nodes[node_id].last_attack[lookup_key] = time()
        log, newly_discovered_nodes, discovered_nodes_value, newly_discovered_credentials = self.__mark_discovered_entities(
            node_id, outcome, log)

        reward += discovered_nodes_value
        reward += newly_discovered_nodes * Reward.NODE_DISCOVERED
        reward += newly_discovered_credentials * Reward.CREDENTIAL_DISCOVERED

        reward -= vulnerability.cost

        if node_info.honeypot_machine:
            reward = 0

        log += 'GOT REWARD : {}\n'.format(vulnerability.reward_string)

        if reward > 0:

            succeed = True
            self._discovered_nodes[node_id].successfull_attack += 1
            if 'FLAG' in vulnerability.reward_string:
                self._captured_flags += 1

        else:

            succeed = False
            self._discovered_nodes[node_id].failed_attack += 1

        return log, succeed, reward, outcome

    def exploit_remote_vulnerability(self,
                                     node_id,
                                     target_node_id,
                                     vulnerability_id,
                                     log
                                     ):
        """Exploit a remote vulnerability."""
        if node_id not in self._environment.network.nodes:
            raise ValueError(
                'Agent does not owned the source node {}'.format(node_id))

        if target_node_id not in self._environment.network.nodes:
            raise ValueError(
                'Invalid target node id {}'.format(target_node_id))

        source_node_info = self._environment.get_node(node_id)
        target_node_info = self._environment.get_node(target_node_id)

        if not source_node_info.agent_installed:
            raise ValueError(
                'Agent does not owned the source node {}'.format(node_id))

        if target_node_id not in self._discovered_nodes:
            raise ValueError(
                'Agent has not discovered the target node {}'.format(target_node_id))

        log, succeeded, reward, outcome = self.__process_outcome(VulnerabilityType.REMOTE,
                                                                 vulnerability_id,
                                                                 target_node_id,
                                                                 target_node_info,
                                                                 True,
                                                                 Penalty.FAILED_REMOTE_EXPLOIT,
                                                                 log
                                                                 )

        if succeeded:
            self.__annotate_edge(
                node_id,
                target_node_id,
                EdgeAnnotation.REMOTE_EXPLOIT)
        
        out = 'Success' if reward > 0 else 'Failed'
        self.report_done_attacks.append(['Remote', node_id, target_node_id, vulnerability_id, '...', out])

        return log, reward, outcome

    def exploit_local_vulnerability(self,
                                    node_id,
                                    vulnerability_id,
                                    log
                                    ):
        """Exploit a local vulnerability."""
        graph = self._environment.network
        if node_id not in graph.nodes:
            raise ValueError('invalid id {}'.format(node_id))

        node_info = self._environment.get_node(node_id)

        if not node_info.agent_installed:
            raise ValueError(
                'Agent does not iwned the node {}'.format(node_id))

        log, _, reward, outcome = self.__process_outcome(VulnerabilityType.LOCAL,
                                                         vulnerability_id,
                                                         node_id,
                                                         node_info,
                                                         True,
                                                         Penalty.FAILED_LOCAL_EXPLOIT,
                                                         log
                                                         )

        out = 'Success' if reward > 0 else 'Failed'
        self.report_done_attacks.append(['Local', '...', node_id, vulnerability_id, '...', out])

        return log, reward, outcome

    def __is_passing_firewall_rules(self, rules, port_name):
        """Check if the actuator is allowed to go through the passing port name providing the firewall rules."""
        for rule in rules:
            if rule.port == port_name:
                if rule.permission == RulePermission.ALLOW:

                    return True

                else:

                    return False

        return False

    def _check_service_running_and_authorized(self,
                                              target_node_data,
                                              port_name,
                                              credential
                                              ):
        """Check if the passing port name correspond to a running service and if the used password is correct."""
        for service in target_node_data.services:

            if service.running and service.name == port_name:

                if credential in service.allowedCredentials:

                    return True

        return False

    def connect_to_remote_machine(self,
                                  source_node_id,
                                  target_node_id,
                                  port_name,
                                  credential,
                                  log
                                  ):
        """Connect to the passing target node id using the providing port name and credential from the given source node id."""
        graph = self._environment.network
        if source_node_id not in graph.nodes:
            raise ValueError('Invalid node id {}'.format(source_node_id))
        if target_node_id not in graph.nodes:
            raise ValueError(
                'Invalid target node id {}'.format(target_node_id))

        target_node = self._environment.get_node(target_node_id)
        source_node = self._environment.get_node(source_node_id)

        if 'hhhhl_' in target_node_id:

            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
            return log, Penalty.USED_HONEYTOKEN, None

        if 'hhhhc_' in credential:

            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
            return log, Penalty.USED_HONEYTOKEN, None

        is_already_discovered = target_node_id in self._discovered_nodes
        already_try_to_connect = (
            port_name, 'connection') in self._discovered_nodes[target_node_id].last_attack
        is_deceptive_element = target_node.decoy_machine or target_node.honeypot_machine

        if is_already_discovered:

            if already_try_to_connect:

                if is_deceptive_element:
                    
                    self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                    return log, Penalty.REPEAT_MISTAKE, None

            if is_deceptive_element:
                
                self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                return log, Penalty.DECOY_OR_HONEYPOT_TOUCHED, None

        if not source_node.agent_installed:
            raise ValueError(
                'Agent does not owned the source node {}'.format(source_node_id))

        if target_node_id not in self._discovered_nodes:
            raise ValueError(
                'Agent has not discovered the target node {}'.format(target_node_id))

        if credential not in self._gathered_credentials:
            raise ValueError(
                'Agent has not discovered credential {}'.format(credential))

        if not self.__is_passing_firewall_rules(
                source_node.firewall.outgoing, port_name):
            log += 'BLOCKED TRAFFIC : source node {} is blocking outgoing traffic on port {}\n'.format(
                source_node_id, port_name)
            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])

            return log, Penalty.BLOCKED_BY_LOCAL_FIREWALL, None

        if not self.__is_passing_firewall_rules(
                target_node.firewall.incoming, port_name):
            log += 'BLOCKED TRAFFIC : source node {} is blocking incoming traffic on port {}\n'.format(
                target_node_id, port_name)
            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])

            return log, Penalty.BLOCKED_BY_REMOTE_FIREWALL, None,

        target_node_is_listening = port_name in [
            i.name for i in target_node.services]

        if not target_node_is_listening:
            log += 'target node {} not listening on port {}\n'.format(
                target_node_id, port_name)
            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
            return log, Penalty.SCANNING_UNOPEN_PORT, None

        else:

            target_node_data = self._environment.get_node(target_node_id)
            was_previously_owned_at = self._discovered_nodes[target_node_id].last_connection

            if target_node_data.status != MachineStatus.RUNING:
                log += 'Target machine not in running state\n'
                self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                return log, Penalty.MACHINE_NOT_RUNNING, None

            if not self._check_service_running_and_authorized(
                    target_node_data, port_name, credential):
                log += 'Invalid credentials supplied\n'
                self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                return log, Penalty.WRONG_PASSWORD, None

            is_already_owned = target_node_data.agent_installed

            if is_already_owned:
                self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                return log, Penalty.REPEAT, lateralMove()

            if target_node_id not in self._discovered_nodes:
                self._discovered_nodes[target_node_id] = NodeTrackingInformation(
                )
                self._discovered_nodes[target_node_id].last_connection = time()

            if was_previously_owned_at is not None and target_node_data is not None and was_previously_owned_at >= target_node_data.last_reimaging:
                self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, 'Failed'])
                return log, Penalty.REPEAT, lateralMove()

            self.__annotate_edge(
                source_node_id,
                target_node_id,
                EdgeAnnotation.LATERAL_MOVE)
            self.__mark_node_as_owned(target_node_id)
            log += 'Infected node {} from {} via {} with credential {}\n'.format(
                target_node_id, source_node_id, port_name, credential)

            self._discovered_nodes[target_node_id].last_attack[(
                port_name, 'connection')] = time()

            if target_node.owned_string:
                log += 'Owned message : {}\n'.format(target_node.owned_string)

                if 'FLAG' in target_node.owned_string:
                    self._captured_flags += 1
            
            reward = target_node_data.value if was_previously_owned_at is None else 0.0
            out = 'Success' if reward > 0 else 'Failed'

            self.report_done_attacks.append(['Connect', source_node_id, target_node_id, port_name, credential, out])

            return log, target_node_data.value if was_previously_owned_at is None else 0.0, lateralMove()
    
    def print_reports(self):
        """Print a dataframe reporting all done attacks."""
        d.display(pd.DataFrame(self.report_done_attacks, columns=['Type', 'Source', 'Target', 'Vulnerability/Port', 'Credential', 'Result']))

    def list_nodes(self):
        """Return a dictionnary where keys are node id and items indicate whether the node is owned or not."""
        d = []
        for node_id, node_info in self.discovered_nodes():
            d.append({
                'id': node_id,
                'status': 'owned' if node_info.agent_installed else 'discovered'
            })

        return d

    def list_remote_attacks(self, node_id):
        """Return a list of remote vulnerability on the providing node id."""
        return self.list_vulnerabilities_in_target(
            node_id, VulnerabilityType.REMOTE)

    def list_local_attacks(self, node_id):
        """Return a list of local vulnerability on the providing node id."""
        return self.list_vulnerabilities_in_target(
            node_id, VulnerabilityType.LOCAL)

    def list_attacks(self, node_id):
        """Return a vulnerabilities list in the passing node id."""
        return self.list_remote_attacks(
            node_id) + self.list_local_attacks(node_id)

    def list_all_attacks(self):
        """Return a list of all type of executable attacks in the network by node."""
        on_owned_nodes = [{'id': n['id'],
                           'status': n['status'],
                           'properties': self._environment.get_node(n['id']).properties,
                           'local_attacks': self.list_local_attacks(n['id']),
                           'remote_attacks': self.list_remote_attacks(n['id'])
                           }
                          for n in self.list_nodes() if n['status'] == 'owned']

        on_discovered_nodes = [{'id': n['id'],
                                'status': n['status'],
                                'properties': self._environment.get_node(n['id']).properties,
                                'local_attacks': None,
                                'remote_attacks': self.list_remote_attacks(n['id'])
                                }
                               for n in self.list_nodes() if n['status'] != 'owned']

        return on_owned_nodes + on_discovered_nodes

    def print_all_attacks(self):
        """Display all attacks."""
        d.display(pd.DataFrame.from_dict(self.list_all_attacks()))

    def get_discovered_nodes_attacks_count(self):
        """Return count of successfull and failed attack for each nodes."""
        ids = self._discovered_nodes.keys()
        return ids, np.array([[n.successfull_attack, n.failed_attack]
                             for n in self._discovered_nodes.values()])

    def add_action(self, gym_action):
        """Update done actions."""
        self._done_actions.add(get_hashable_action(gym_action))

    def get_done_actions(self):
        """Return tried actions."""
        return self._done_actions


class DefenderAgentActions:
    """Class for the environment defender actuator."""

    def __init__(self, environment):
        """Init params."""
        self.nodes_reimaging_progress = dict()
        self.__network_availability = 1.0
        self._environment = environment

    def network_availability(self):
        """Return the network availability."""
        return self.__network_availability

    def reimaging_node(self, node_id):
        """Start reimaging the provinding node."""
        self.nodes_reimaging_progress[node_id] = Reimaging.REIMAGING_DURATION

        node_info = self._environment.get_node(node_id)
        assert node_info.reimagable, 'Node {} is not reimagable'.format(
            node_id)

        node_info.agent_installed = False
        node_info.privilege_level = PrivilegeLevel.NoAcces
        node_info.status = MachineStatus.IMAGING
        node_info.last_reimaging = time()
        self._environment.network.nodes[node_id].update({'data': node_info})

    def on_attacker_step_taken(self, log):
        """Update reimaging durations and compute the current network availability."""
        for node_id in list(self.nodes_reimaging_progress.keys()):
            reimaging_steps = self.nodes_reimaging_progress[node_id]
            if reimaging_steps > 0:
                self.nodes_reimaging_progress[node_id] -= 1
            else:
                log += 'Machine re-imaging completed : {}'.format(node_id)
                node_data = self._environment.get_node(node_id)
                node_data.status = MachineStatus.RUNING
                self.nodes_reimaging_progress.pop(node_id)

        total_node_weights = 0
        network_node_availability = 0
        for node_id, node_info in self._environment.nodes():
            total_service_weights = 0
            running_service_weights = 0
            for service in node_info.services:
                total_service_weights += service.sla_weight
                running_service_weights += service.sla_weight * \
                    int(service.running)

            if node_info.status == MachineStatus.RUNING:
                adjusted_node_availability = (
                    1 + running_service_weights) / (1 + total_service_weights)
            else:
                adjusted_node_availability = 0.0

            total_node_weights += node_info.sla_weight
            network_node_availability += adjusted_node_availability * node_info.sla_weight

        self.__network_availability = network_node_availability / total_node_weights
        assert(self.__network_availability <=
               1.0 and self.__network_availability >= 0.0)

        return log

    def override_firewall_rules(
            self, node_id, port_name, incoming, permission):
        """Rewrite or add a rule permission to a providing firewall at a given port name and node id."""
        node_data = self._environment.get_node(node_id)
        rules = node_data.firewall.incoming if incoming else node_data.firewall.outgoing
        matching_rules = [r for r in rules if r.port_name == port_name]

        if matching_rules:
            for r in matching_rules:
                r.permission = permission

        else:
            new_rule = FirewallRule(port_name, permission)
            if incoming:
                node_data.firewall.incoming = [
                    new_rule] + node_data.firewall.incoming
            else:
                node_data.firewall.outgoing = [
                    new_rule] + node_data.firewall.outgoing

    def block_traffic(self, node_id, port_name, incoming):
        """Block the traffic at a providing node and port name."""
        return self.override_firewall_rules(
            node_id, port_name, incoming, RulePermission.BLOCK)

    def allow_traffic(self, node_id, port_name, incoming):
        """Allow the traffic at a providing node and port name."""
        return self.override_firewall_rules(
            node_id, port_name, incoming, RulePermission.ALLOW)

    def stop_service(self, node_id, port_name):
        """Stop a machine service."""
        node_data = self._environment.get_node(node_id)
        assert node_data.status == MachineStatus.RUNING, "Machine must be running to stop a service"

        for service in node_data.services:
            if service.name == port_name:
                service.running = False

    def start_service(self, node_id, port_name):
        """Start a machine service."""
        node_data = self._environment.get_node(node_id)
        assert node_data.status == MachineStatus.RUNING, "Machine must be running to start a service"

        for service in node_data.services:
            if service.name == port_name:
                service.running = True
