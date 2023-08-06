"""This file provides an autonomous defenser based on scanning with less or more luck to detect infected nodes."""

import numpy as np
from ...utils.objects_and_global_functions import *


class ScanAndReimageCompromiseMachines:
    """The core class."""

    def __init__(self, probability, scan_capacity, scan_frequency):
        """Init the scanner.

        Provide a detection probability, a number of scannable nodes each
        done scan and a number to determinate iterations interval to scan.
        """
        self.probability = probability
        self.scan_capacity = scan_capacity
        self.scan_frequency = scan_frequency

    def step(self, env, actuator, iteration_count, log):
        """Scan the network with respect to probability, scan_capacity, scan_frequency parameters."""
        if iteration_count % self.scan_frequency == 0:

            scanned_nodes = np.random.choice(
                env.network.nodes, size=self.scan_capacity)

            for node_id in scanned_nodes:

                node_info = env.get_node(node_id)
                if node_info.status == MachineStatus.RUNNIG and node_info.agent_installed:

                    if np.random.random() <= self.probability:
                        if node_info.reimagable:
                            log += 'Defender detected malware, reimaging node {}\n'.format(
                                node_id)
                            actuator.reimaging_node(node_id)
                        else:
                            log += 'Defender detected malware, but node {} cannot be reimagable\n'.format(
                                node_id)

        return log
