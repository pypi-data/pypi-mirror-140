"""Provide methods to allow the user to play at CyberBattle."""

from ..env.env_generation.actions import AgentActions
from .objects_and_global_functions import *

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import IPython.core.display as d


class Player:
    """Core class."""

    def __init__(self, identifiers, cyber_env, max_flag):
        """Display possible actions and describe the infected node."""
        self.identifiers = identifiers
        self.actuator = AgentActions(cyber_env)
        self.env = cyber_env
        self.log = ''
        self.rewards = []
        self.total_reward = 0
        self.credentials = set()
        self.max_flag = max_flag

        self.id_and_display()
        self.describe_infected_node()
        self.plot_nodes()
        plt.show()
    
    def id_and_display(self):
        "Display possible actions."
        self.local_vulnerabilities = self.identifiers.local_vulnerabilities
        self.remote_vulnerabilities = self.identifiers.remote_vulnerabilities
        self.ports = self.identifiers.ports
        self.n_local = len(self.local_vulnerabilities)
        self.n_remote = len(self.remote_vulnerabilities)
        self.n_port = len(self.ports)

        local_id = {i: l for i, l in enumerate(self.local_vulnerabilities)}
        remote_id = {i + self.n_local: r for i, r in enumerate(self.remote_vulnerabilities)}
        ports_id = {i + self.n_local +self. n_remote: p for i, p in enumerate(self.ports)}

        self.actions = {**local_id, **remote_id, **ports_id}

        print('Your possible actions are as follows:\n')
        for i, a in self.actions.items():

            if i < self.n_local + self.n_remote:

                print('Execute the action {} by entering the id : {}'.format(a, i))
                if i < self.n_local:

                    print('This action can be performed locally\n')
                
                elif i < self.n_remote + self.n_local:

                    print('This action can be performed remotely\n')
            
            else:

                print('Entering the id {} means that you want to connect to a machine through the {} port'.format(i, a))

    def describe_infected_node(self):
        """Describe the manually infected node."""
        nodes = self.env.nodes()

        for node, node_data in nodes:

            if node_data.agent_installed:

                print('\nYou have manually infected the {} node.\n'.format(node))
    
    def get_node_color(self, node_info):
        """Return 'red' if node is infected and 'green' otherwise."""
        if node_info.agent_installed:
            return 'red'
        else:
            return 'green'

    def plot_nodes(self):
        """Plot the sub-graph of nodes either so far discovered  (their ID is knowned by the agent) or owned (i.e. where the attacker client is installed)."""
        discovered_nodes = [node_id for node_id, _ in self.actuator.discovered_nodes()]
        sub_graph = self.env.network.subgraph(discovered_nodes)
        print('\nDiscovered network:\n')
        nx.draw(sub_graph,
                with_labels=True,
                node_color=[self.get_node_color(self.env.get_node(i)) for i in sub_graph.nodes])

    def print_credential_cache(self):
        """Print the current credential cache."""
        d.display(pd.DataFrame(self.credentials, columns=['Node', 'Port', 'Credential']))
    
    def run_attack(self, target_node, source_node=None, action_id=None, credential=None):

        if not source_node:

            if action_id >= self.n_local:

                print("The provided action id {} can't be performed locally.".format(action_id))
                return

            log, reward, outcome = self.actuator.exploit_local_vulnerability(
                node_id=target_node,
                vulnerability_id=self.local_vulnerabilities[action_id],
                log=self.log)
            if isinstance(outcome, LeakedCredentials):
                for cred in outcome.credentials:
                    self.credentials.add((cred.node, cred.port, cred.credential))
            self.rewards.append(reward)
            self.total_reward += reward
        
        action_id -= self.n_local
        
        if source_node:

            if not credential:

                if action_id >= self.n_remote:

                    print("The provided action id {} can't be performed remotely.".format(action_id))
                    return
                
                log, reward, outcome = self.actuator.exploit_remote_vulnerability(
                    node_id=source_node,
                    target_node_id=target_node,
                    vulnerability_id=self.remote_vulnerabilities[action_id],
                    log=self.log
                )

                if isinstance(outcome, LeakedCredentials):
                    for cred in outcome.credentials:
                        self.credentials.add((cred.node, cred.port, cred.credential))
                self.rewards.append(reward)
                self.total_reward += reward
            
            else:

                action_id -= self.n_remote

                if action_id >= self.n_port:

                    print("Unknow id {}".format(action_id))
                    return
                
                log, reward, outcome = self.actuator.connect_to_remote_machine(
                    source_node_id=source_node,
                    target_node_id=target_node,
                    port_name=self.ports[action_id],
                    credential=credential,
                    log=self.log
                )
                self.rewards.append(reward)
                self.total_reward += reward

        current_log = log.lstrip(self.log[:-1])
        print(current_log)
        self.log = log 

        if reward > 0:
            print('Congratulations, you earned {} !\n'.format(reward))

        print('Total reward : {}\n'.format(self.total_reward))
        print('Report of what you have done up to now:\n')
        self.actuator.print_reports()
        print('\nReminding your credential cache:\n')
        self.print_credential_cache()
        self.plot_nodes()
        plt.show()

        if self.actuator._captured_flags == self.max_flag:

            print('Congratulations ! You captured all the flags ! :D\n')
            plt.clf()
            plt.title('Summary of your rewards')
            plt.xlabel('Step')
            plt.ylabel('Cumulative rewards')
            plt.plot(range(len(self.rewards)), np.cumsum(self.rewards))
            plt.show()

            print('Summary of the simulations : \n\n{}'.format(self.log))

            self.reset()
    
    def reset(self):
        """Reset all attributes."""
        self.credentials = set()
        self.total_reward = 0
        self.actuator = AgentActions(self.env)
        self.rewards = []
        self.log = ''