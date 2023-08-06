"""Agent_wrapper provide a class kit to transform the moving state space into a constant input for agents.

Notice we won't use these classes for the GNN learner
"""


import random
import numpy as np
from ...utils.objects_and_global_functions import sourcenode_of_action, node_of_action, get_adjacent_matrix, PrivilegeLevel
from gym import spaces, Wrapper
from typing import List

Window_size = 3


class Feature(spaces.MultiDiscrete):
    """The core class."""

    def __init__(self, env_properties, nvec):
        """Provide the environment bounds and vector number."""
        self.env_properties = env_properties
        super().__init__(nvec)

    def flat_size(self):
        """Return the flat dimension."""
        return np.prod(self.nvec)

    def name(self):
        """Return the feature name."""
        p = len(type(Feature(self.env_properties, [])).__name__) + 1
        return type(self).__name__[p:]

    def get(self, a, node):
        """Return will return the feature vector representation."""
        raise NotImplementedError


class FeatureEncoder(Feature):
    """Initialize an instance with a feature selection.

    Encode a list of feature as a unique index.
    """

    feature_selection: List[Feature]

    def vector_to_index(self, feature_vector):
        """Encode a vector as an index."""
        raise NotImplementedError

    def feature_vector_of_observation_at(self, a, node):
        """Return the corresponding feature vector to the current observation."""
        return np.concatenate([f.get(a, node) for f in self.feature_selection])

    def encode(self, a, node=None):
        """Encode the feature as an index."""
        feature_vector_concat = self.feature_vector_of_observation_at(a, node)

        return self.vector_to_index(feature_vector_concat)

    def encode_at(self, a, node):
        """Encode the feature as an index with a node context."""
        feature_vector_concat = self.feature_vector_of_observation_at(a, node)

        return self.vector_to_index(feature_vector_concat)

    def get(self, a, node):
        """Return the feature vector."""
        return np.array(self.encode(a, node))

    def name(self):
        """Return a name for the feature encoding."""
        n = ', '.join([f.name() for f in self.feature_selection])

        return '[{}]'.format(n)


class Feature_active_node_age(Feature):
    """Provide informations about how the node was discovered recently."""

    def __init__(self, env_bounds):
        """One dimensional vector with maximum_node_count possible values."""
        super().__init__(env_bounds, [env_bounds.maximum_node_count])

    def get(self, stateaugmentation, node):
        """Return reversed indice of node with respect to discovered node count."""
        assert node is not None

        discovered_node_count = len(
            stateaugmentation.observation.discovered_nodes_properties
        )

        assert node < discovered_node_count

        return np.array([discovered_node_count - node - 1])


class Feature_active_node_properties(Feature):
    """Allow the agent to have a look at discovered properties."""

    def __init__(self, env_bounds):
        """Property_count dimensional vector with binary elements."""
        super().__init__(env_bounds, [2] * env_bounds.property_count)

    def get(self, stateaugmentation, node):
        """Return the vector where 1 means the property is discovered and 0 otherwise."""
        assert node is not None

        node_prop = stateaugmentation.observation.discovered_nodes_properties

        assert node < len(node_prop)

        return np.int32((1 + node_prop[node]) / 2)


class Feature_discovered_nodeproperties_sliding(Feature):
    """Allow the agent to receive node properties seen in last window_size cache entries."""

    def __init__(self, env_bounds):
        """Property_count dimensional vector with binary elements."""
        super().__init__(env_bounds, [2] * env_bounds.property_count)

    def get(self, stateaugmentation, node):
        """Return an array of shape (Window_size,). 1 means we discover a property in the last discovered."""
        node_prop = np.array(
            stateaugmentation.observation.discovered_nodes_properties
        )
        node_prop_window = node_prop[- Window_size:, :]
        node_prop_window_remapped = np.int32((1 + node_prop_window) / 2)

        countby = np.sum(node_prop_window_remapped, axis=0)

        return np.where(countby > 0, 1, 0)


class Feature_discovered_notowned_node_count(Feature):
    """Count discovered not owned node."""

    def __init__(self, env_bounds, clip):
        """Clip is an integer only if we want to check only a few proportions among discovered nodes."""
        self.clip = env_bounds.maximum_node_count if clip is None else clip
        super().__init__(env_bounds, [self.clip + 1])

    def get(self, stateaugmentation, node):
        """Return the count discovered not owned node."""
        node_props = stateaugmentation.observation.discovered_nodes_properties
        discovered = len(node_props)

        owned = np.count_nonzero(np.all(node_props != 0, axis=1))

        return [min(discovered - owned, self.clip)]


class Feature_discovered_ports_sliding(Feature):
    """Ports seen in last window_size cache entries."""

    def __init__(self, env_bounds):
        """Prepare a port_count dimensional vector with binary elements."""
        super().__init__(env_bounds, [2] * env_bounds.port_count)

    def get(self, stateaugmentation, node):
        """Return last window_size cache entries."""
        observation = stateaugmentation.observation
        credential_cache_matrix = observation.credentials_cache_matrix
        know_credports = np.zeros(self.env_properties.port_count)
        idxs = credential_cache_matrix[- Window_size:, 1].astype(np.int)
        know_credports[idxs] = 1

        return know_credports


class Feature_discovered_credentials(Feature):
    """Discovered credentials applyable on each discovered nodes."""

    def __init__(self, env_bounds):
        """Prepare a maximum_node_count * maximum_total_credentials dimensional vector with binary elements."""
        super().__init__(
            env_bounds,
            [2] *
            env_bounds.maximum_total_credentials *
            env_bounds.maximum_node_count)

    def get(self, stateaugmentation, node):
        """Return discovered credentials applyable on discovered nodes."""
        observation = stateaugmentation.observation
        credential_cache_matrix = observation.credentials_cache_matrix
        discovered_node_count = observation.discovered_node_count
        know_creds = np.ones(
            (self.env_properties.maximum_node_count,
             self.env_properties.maximum_total_credentials)) * -1
        know_creds[:discovered_node_count, :] = 0
        for i, c in enumerate(credential_cache_matrix):
            idx = int(c[0])
            know_creds[idx, i] = 1

        return know_creds


class Feature_privilegelevel(Feature):
    """Privilege level at the providing node."""

    def __init__(self, env_bounds):
        """Prepare the element which will inform the privilege level of the agent."""
        super().__init__(
            env_bounds, [
                PrivilegeLevel.MAXIMUM + 1] * env_bounds.maximum_node_count)

    def get(self, stateaugmentation, node):
        """Return privilege level at the providing node."""
        observation = stateaugmentation.observation
        privilegelevels = observation.nodes_privilegelevel
        privilegelevels_global = np.ones(
            self.env_properties.maximum_node_count) * -1
        for i, p in enumerate(privilegelevels):
            privilegelevels_global[i] = p

        return privilegelevels_global


class Feature_active_properties(Feature):
    """Allow the agent to have a look at discovered properties on each nodes."""

    def __init__(self, env_bounds):
        """Prepare a maximum_node_count * maximum_total_credentials dimensional vector with binary elements."""
        super().__init__(
            env_bounds,
            [2] *
            env_bounds.property_count *
            env_bounds.maximum_node_count)

    def get(self, stateaugmentation, node):
        """Return discovered properties on each nodes."""
        observation = stateaugmentation.observation
        discovered_node_properties = np.int32(
            (1 + observation.discovered_nodes_properties) / 2)
        props = np.ones(
            (self.env_properties.maximum_node_count,
             self.env_properties.property_count)) * -1
        props[:discovered_node_properties.shape[0],
              :] = discovered_node_properties

        return props


class ConcatFeatures(Feature):
    """Concatenate a list of features into a simple feature."""

    def __init__(self, env_bounds, feature_selection):
        """Feature selection is a list of features."""
        self.feature_selection = feature_selection
        self.dim_sizes = np.concatenate([f.nvec for f in feature_selection])
        super().__init__(env_bounds, [self.dim_sizes])

    def get(self, stateaugmentation, node):
        """Return a concatenation of feature vectors."""
        feature_vector = [
            f.get(stateaugmentation, node)
            for f in self.feature_selection
        ]

        return np.concatenate(feature_vector)


class HashEncoding(FeatureEncoder):
    """Hash a feature."""

    def __init__(self, env_bounds, feature_selection, hash_size):
        """Provide a hash_size to determinate value possibilities to hash."""
        self.feature_selection = feature_selection
        self.hash_size = hash_size
        super().__init__(env_bounds, [hash_size])

    def flat_size(self):
        """Return the hash_size."""
        return self.hash_size

    def vector_to_index(self, feature_vector):
        """Return the hash encoding."""
        return hash(str(feature_vector)) % self.hash_size


class RavelEncoding(FeatureEncoder):
    """Compute an index by raveling the index of vector features selection."""

    def __init__(self, env_bounds, feature_selection):
        """Compute dim_sizes and ravel it."""
        self.feature_selection = feature_selection
        self.dim_sizes = np.concatenate([f.nvec for f in feature_selection])
        self.raveled_size = np.prod(self.dim_sizes)

        assert np.shape(self.raveled_size) == ()

        super().__init__(env_bounds, [self.raveled_size])

    def vector_to_index(self, feature_vector):
        """Compute the raveling index."""
        assert len(self.dim_sizes) == len(feature_vector)

        index = np.ravel_multi_index(feature_vector, self.dim_sizes)

        assert index < self.raveled_size

        return index

    def unravel_index(self, index):
        """Get the older index of the features vector."""
        return np.unravel_index(index, self.dim_sizes)


# class StateAugmentation to get the observation during the simulation


class StateAugmentation:
    """Class to distribute the observation to the agent each iterations."""

    def __init__(self, observation):
        """Save observation."""
        self.observation = observation

    def on_step(self, action, reward, done, observation):
        """Save observation."""
        self.observation = observation

    def on_reset(self, observation):
        """Save observation."""
        self.observation = observation


class AbstractAction(Feature):
    """This class is a tool to convert a chosen action by the agent to a readable action in the gym environment and inversely."""

    def __init__(self, env_bounds):
        """Compute number of executable actions with respect to fixed bounds."""
        self.n_local_actions = env_bounds.local_attacks_count
        self.n_remote_actions = env_bounds.remote_attacks_count
        self.n_connect_actions = env_bounds.port_count
        self.n_actions = self.n_local_actions + self.n_remote_actions \
            + self.n_connect_actions
        super().__init__(env_bounds, [self.n_actions])

    def specialize_to_gymaction(
        self,
        source_node,
        observation,
        abstract_action_index,
        log
    ):
        """Chosen agent action -> readable gym action."""
        nodes_prop = np.array(observation.discovered_nodes_properties)

        if abstract_action_index < self.n_local_actions:
            return log, {
                'local_vulnerability': np.array(
                    [source_node, abstract_action_index], dtype=int
                )
            }

        abstract_action_index -= self.n_local_actions
        if abstract_action_index < self.n_remote_actions:
            discovered_nodes_count = len(nodes_prop)

            if discovered_nodes_count <= 1:
                return log, None

            target = (
                source_node + 1 + np.random.choice(discovered_nodes_count - 1)
            ) % discovered_nodes_count

            return log, {
                'remote_vulnerability': np.array(
                    [source_node, target, abstract_action_index], dtype=int
                )
            }

        abstract_action_index -= self.n_remote_actions
        discovered_credentials = np.array(observation.credentials_cache_matrix)
        n_discovered_creds = len(discovered_credentials)
        if n_discovered_creds <= 0:

            return log, None

        nodes_not_owned = np.nonzero(observation.nodes_privilegelevel == 0)[0]

        match_port = discovered_credentials[:, 1] == abstract_action_index
        match_port_indices = np.where(match_port)[0]

        credential_indices_choices = [
            c for c in match_port_indices
            if discovered_credentials[c, 0] in nodes_not_owned
        ]

        if credential_indices_choices:
            log += 'Found matching cred in the credential matrix\n'

        else:
            log += 'no cred matching requested port, \
                trying instead creds used to access other ports\n'
            credential_indices_choices = [
                i for (i, n) in enumerate(discovered_credentials[:, 0])
                if n in nodes_not_owned
            ]

            if credential_indices_choices:
                log += 'found cred in the credential cache \
                    without matching port name'

            else:
                log += 'no cred to use from the credential cache'
                return log, None

        cred = random.choice(credential_indices_choices)
        target = discovered_credentials[cred, 0]
        return log, {
            'connect': np.array(
                [source_node, target, abstract_action_index, cred], dtype=int
            )
        }

    def abstract_from_gymaction(self, gym_action):
        """Readable gym action -> chosen agent action."""
        if 'local_vulnerability' in gym_action:

            return gym_action['local_vulnerability'][1]

        elif 'remote_vulnerability' in gym_action:

            return gym_action['remote_vulnerability'][2] \
                + self.n_local_actions

        assert 'connect' in gym_action

        a = gym_action['connect'][2] \
            + self.n_remote_actions \
            + self.n_local_actions

        assert a < self.n_actions

        return np.int32(a)


class AbstractActionGNN(Feature):
    """This class is a tool to convert a chosen action by the GNN agent to a readable action in the gym environment and inversely."""

    def __init__(self, env_bounds):
        """Compute number of executable actions with respect to fixed bounds."""
        self.n_local_actions = env_bounds.local_attacks_count
        self.n_remote_actions = env_bounds.remote_attacks_count
        self.n_connect_actions = env_bounds.port_count
        self.n_actions = self.n_local_actions + self.n_remote_actions \
            + self.n_connect_actions
        super().__init__(env_bounds, [self.n_actions])

    def specialize_to_gymaction(
        self,
        action_node,
        observation,
        abstract_action_index,
        log
    ):
        """Chosen agent action -> readable gym action."""
        nodes_prop = np.array(observation.discovered_nodes_properties)

        if abstract_action_index < self.n_local_actions:
            return log, {
                'local_vulnerability': np.array(
                    [action_node, abstract_action_index], dtype=int
                )
            }

        abstract_action_index -= self.n_local_actions
        source = random.choice(np.nonzero(observation.nodes_privilegelevel)[0])
        if abstract_action_index < self.n_remote_actions:
            discovered_nodes_count = len(nodes_prop)

            if discovered_nodes_count <= 1:
                return log, None

            return log, {
                'remote_vulnerability': np.array(
                    [source, action_node, abstract_action_index], dtype=int
                )
            }

        abstract_action_index -= self.n_remote_actions
        discovered_credentials = np.array(observation.credentials_cache_matrix)
        n_discovered_creds = len(discovered_credentials)
        if n_discovered_creds <= 0:

            return log, None

        match_target_node_creds = observation.credentials_cache_matrix[
            :, 0] == abstract_action_index
        credential_indices_choices = np.where(match_target_node_creds)[0]

        if not credential_indices_choices:
            log += 'no cred to use from the credential cache'
            return log, None

        cred = np.random.choice(credential_indices_choices)
        return log, {
            'connect': np.array(
                [source, action_node, abstract_action_index, cred], dtype=int
            )
        }

    def abstract_from_gymaction(self, gym_action):
        """Readable gym action -> chosen agent action."""
        if 'local_vulnerability' in gym_action:

            return gym_action['local_vulnerability'][1]

        elif 'remote_vulnerability' in gym_action:

            return gym_action['remote_vulnerability'][2] \
                + self.n_local_actions

        assert 'connect' in gym_action

        a = gym_action['connect'][2] \
            + self.n_remote_actions \
            + self.n_local_actions

        assert a < self.n_actions

        return np.int32(a)


class ActionTrackingStateAugmentation(StateAugmentation):
    """Count succesfull and failed actions."""

    def __init__(self, env_bounds, observation):
        """Prepare count vectors with respect to environment bounds."""
        self.aa = AbstractAction(env_bounds)
        self.success_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.failed_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.env_properties = env_bounds
        super().__init__(observation)

    def on_step(self, action, reward, done, observation):
        """Each step -> increment for each action and each source of action."""
        node = sourcenode_of_action(action)
        abstract_action = self.aa.abstract_from_gymaction(action)
        if reward > 0:
            self.success_action_count[node, abstract_action] += 1

        else:
            self.failed_action_count[node, abstract_action] += 1

        super().on_reset(observation)

    def on_reset(self, observation):
        """Reset -> rest count at 0."""
        env_bounds = self.env_properties
        self.success_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.failed_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        super().on_reset(observation)


class ActionTrackingStateAugmentationGNN(StateAugmentation):
    """Count succesfull and failed actions."""

    def __init__(self, env_bounds, observation):
        """Prepare count vectors with respect to environment bounds."""
        self.aa = AbstractAction(env_bounds)
        self.discovered_node_count = observation.discovered_node_count
        self.adj_matrix = get_adjacent_matrix(observation)
        self.success_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.failed_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.env_properties = env_bounds
        super().__init__(observation)

    def on_step(self, action, reward, done, observation):
        """Each step -> increment for each action and each source of action."""
        node = node_of_action(action)
        self.discovered_node_count = observation.discovered_node_count
        self.adj_matrix = get_adjacent_matrix(observation)
        abstract_action = self.aa.abstract_from_gymaction(action)
        if reward > 0:
            self.success_action_count[node, abstract_action] += 1

        else:
            self.failed_action_count[node, abstract_action] += 1

        super().on_reset(observation)

    def on_reset(self, observation):
        """Reset -> rest count at 0."""
        env_bounds = self.env_properties
        self.success_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        self.failed_action_count = np.zeros(
            (env_bounds.maximum_node_count, self.aa.n_actions)
        )
        super().on_reset(observation)


class Feature_succes_actions_at_node(Feature):
    """Provide to the agent the successfull attack number taken the node as source."""

    max_action_count = 100

    def __init__(self, env_bounds):
        """Create a n_actions dimensional vector with max_action_count possible elements."""
        super().__init__(
            env_bounds,
            [self.max_action_count] * AbstractAction(env_bounds).n_actions
        )

    def get(self, trackingstateaugmentation, node):
        """Return the successfull attack number for the passing node."""
        return np.minimum(
            trackingstateaugmentation.success_action_count[node, :],
            self.max_action_count - 1
        )


class Feature_failed_actions_at_node(Feature):
    """Provide to the agent the failed attack number taken the node as source."""

    max_action_count = 100

    def __init__(self, env_bounds):
        """Create a n_actions dimensional vector with max_action_count possible elements."""
        super().__init__(
            env_bounds,
            [self.max_action_count] * AbstractAction(env_bounds).n_actions
        )

    def get(self, trackingstateaugmentation, node):
        """Return the failed attack number for the passing node."""
        return np.minimum(
            trackingstateaugmentation.failed_action_count[node, :],
            self.max_action_count - 1
        )


class Feature_succes_actions(Feature):
    """Provide to the agent the success attack number on each ndoes."""

    max_action_count = 100

    def __init__(self, env_bounds):
        """Init."""
        self.n_actions = AbstractAction(env_bounds).n_actions
        super().__init__(env_bounds, [self.max_action_count] *
                         AbstractAction(env_bounds).n_actions *
                         env_bounds.maximum_node_count)

    def get(self, trackingstateaugmentation, node):
        """Return the success attack number for all discovered nodes."""
        discovered_node_count = trackingstateaugmentation.discovered_node_count
        success_attacks = np.ones(
            (self.env_properties.maximum_node_count, self.n_actions)) * -1
        success_attacks[:discovered_node_count] = np.minimum(
            trackingstateaugmentation.success_action_count[:discovered_node_count],
            self.max_action_count - 1
        )

        return success_attacks


class Feature_failed_actions(Feature):
    """Provide to the agent the failed attack number on each ndoes."""

    max_action_count = 100

    def __init__(self, env_bounds):
        """Init."""
        self.n_actions = AbstractAction(env_bounds).n_actions
        super().__init__(env_bounds, [self.max_action_count] *
                         AbstractAction(env_bounds).n_actions *
                         env_bounds.maximum_node_count)

    def get(self, trackingstateaugmentation, node):
        """Return the failed attack number for all discovered nodes."""
        discovered_node_count = trackingstateaugmentation.discovered_node_count
        failed_attacks = np.ones(
            (self.env_properties.maximum_node_count, self.n_actions)) * -1
        failed_attacks[:discovered_node_count] = np.minimum(
            trackingstateaugmentation.failed_action_count[:discovered_node_count],
            self.max_action_count - 1
        )

        return failed_attacks


class Feature_weights(Feature):
    """Adjacent matrix."""

    def __init__(self, env_bounds):
        """Init."""
        super().__init__(
            env_bounds,
            [3] *
            env_bounds.maximum_node_count *
            env_bounds.maximum_node_count)

    def get(self, trackingstateaugmentation, node):
        """Return the adjacent matrix."""
        adj = np.ones((self.env_properties.maximum_node_count,
                      self.env_properties.maximum_node_count)) * -1
        discovered_node_count = trackingstateaugmentation.discovered_node_count
        adj[:discovered_node_count,
            :discovered_node_count] = trackingstateaugmentation.adj_matrix

        return adj


class HstackFeature(Feature):
    """Concatenate a list of features into a simple feature."""

    def __init__(self, env_bounds, feature_selection):
        """Feature selection is a list of features."""
        self.feature_selection = feature_selection
        self.dim_sizes = np.concatenate([f.nvec for f in feature_selection])
        super().__init__(env_bounds, [self.dim_sizes])

    def get(self, stateaugmentation, node):
        """Return a concatenation of feature vectors."""
        feature_vector = []

        for f in self.feature_selection:
            v = f.get(stateaugmentation, node)
            if len(v.shape) == 1:
                v = np.expand_dims(v, axis=-1)
            feature_vector.append(v)

        return np.hstack(feature_vector)


class AgentWrapper(Wrapper):
    """Wrappe environment for the agent."""

    def __init__(self, env, state):
        """Args: env is a CyberBattleEnv object and state is ActionTrackingStateAugmentation object."""
        super().__init__(env)
        self.state = state

    def step(self, action, log):
        """Execute action in the environment and update the ActionTrackingStateAugmentation."""
        log, observation, reward, done, info = self.env.step(action, log)
        self.state.on_step(action, reward, done, observation)

        return log, observation, reward, done, info

    def reset(self):
        """Reset action in the environment and update the ActionTrackingStateAugmentation."""
        observation = self.env.reset()
        self.state.on_reset(observation)

        return observation
