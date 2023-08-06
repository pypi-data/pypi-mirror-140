"""Qlearner where q values are updates with respect to the Bellman equation.

In our cyber case, two Q matrix are updates. The first one had to determinate
the best attack source and the second one the best attack providing attack sources.
"""

import numpy as np
from .utils.agent_wrapper import *
from .RandomCredLookUp import *
from ..utils.objects_and_global_functions import *


class QTL:
    """Class to provide both QMatrix."""

    def __init__(self, qattack, qsource):
        """Init both matrix."""
        self.qattack = qattack
        self.qsource = qsource


class ChosenActionMetadata:
    """Track an action."""

    def __init__(self,
                 Q_source_state,
                 Q_source_expected,
                 Q_attack_expected,
                 source_node,
                 source_node_encoding,
                 abstract_action,
                 Q_attack_state):
        """Track elements seen at t for pushing it at t + 1 after the next environment step."""
        self.Q_source_state = Q_source_state
        self.Q_attack_state = Q_attack_state
        self.Q_source_expected = Q_source_expected
        self.Q_attack_expected = Q_attack_expected
        self.source_node = source_node
        self.source_node_encoding = source_node_encoding
        self.abstract_action = abstract_action


class QMatrix:
    """The core object of this file."""

    def __init__(self, name, state_space, action_space, qm=None):
        """Init hyper parameters."""
        self.name = name
        self.state_space = state_space
        self.action_space = action_space

        self.state_dim = np.prod(state_space.nvec)
        self.action_dim = np.prod(action_space.nvec)

        self.qm = self.clear() if not qm else qm

        self.last_error = 0

    def shape(self):
        """Return the state space and action space dimensions."""
        return (self.state_dim, self.action_dim)

    def clear(self):
        """Reset q values of the QMatrix at 0."""
        self.qm = np.zeros(self.shape())

        return self.qm

    def print(self):
        """Print name, action and state space and their shapes."""
        print("{} \n state : {} \n action : {} \n shape = {}".format(
            self.name, self.state_space, self.action_space, self.shape()))

    def update(self, current_state, action, next_state,
               reward, gamma, learning_rate):
        """Update q values with respect to the Bellman equation."""
        maxq_atnext, _ = random_argmax(self.qm[next_state, :])

        error = reward + gamma * maxq_atnext - self.qm[current_state, action]
        self.qm[current_state, action] += learning_rate * error

        self.last_error = error ** 2

        return self.qm[current_state, action]

    def exploit(self, features, percentile):
        """Return potential actions exploting the Q matrix selecting q values with a percentil."""
        expected_q, action = random_argtop_percentile(
            self.qm[features, :], percentile)

        return int(action), expected_q


class QlearnAttackSource(QMatrix):
    """The QMatrix to determinate the attack source."""

    def __init__(self, env_bounds, qm=None):
        """Init needed features."""
        self.env_bounds = env_bounds

        self.state_space = HashEncoding(env_bounds, [
            Feature_discovered_ports_sliding(env_bounds),
            Feature_discovered_nodeproperties_sliding(env_bounds),
            Feature_discovered_notowned_node_count(env_bounds, 3)
        ], 10000)

        self.action_space = RavelEncoding(
            env_bounds, [Feature_active_node_properties(env_bounds)])

        super().__init__("attack_source", self.state_space, self.action_space, qm)


class QlearnBestAttackAtSource(QMatrix):
    """The QMatrix to determinate the best attack providing a source."""

    def __init__(self, env_bounds, qm=None):
        """Init needed features."""
        self.state_space = HashEncoding(env_bounds, [
            Feature_active_node_properties(env_bounds),
            Feature_active_node_age(env_bounds)
        ], 10000)

        self.action_space = AbstractAction(env_bounds)

        super().__init__("attack_at_source", self.state_space, self.action_space, qm)


class LossEval:
    """Track the model loss."""

    def __init__(self, qmatrix):
        """Init both trackers."""
        self.qmatrix = qmatrix
        self.this_episode = []
        self.all_episode = []

    def new_episode(self):
        """Reset errors."""
        self.this_episode = []

    def end_of_iteration(self, t, done):
        """Append the last done error."""
        self.this_episode.append(self.qmatrix.last_error)

    def current_episode_loss(self):
        """Return the average loss during the epoch."""
        return np.average(self.this_episode)

    def end_of_episode(self, i_episode, t):
        """Append all losses."""
        self.all_episode.append(self.current_episode_loss())


class QTabularLearner:
    """The core class."""

    def __init__(self,
                 env_bounds,
                 gamma,
                 learning_rate,
                 exploit_percentile=100,
                 trained=None):
        """Init hyper parameters."""
        if trained:
            self.qsource = trained.qsource
            self.qattack = trained.qattack

        else:
            self.qsource = QlearnAttackSource(env_bounds)
            self.qattack = QlearnBestAttackAtSource(env_bounds)

        self.loss_qsource = LossEval(self.qsource)
        self.loss_qattack = LossEval(self.qattack)
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.exploit_percentile = exploit_percentile
        self.credcache_policy = CredentialCacheExploiter()

    def on_step(self, wrapped_env, observation,
                reward, done, info, action_metadata):
        """Update both QMatrix."""
        agent_state = wrapped_env.state

        after_toplevel_state = self.qsource.state_space.encode(agent_state)
        self.qsource.update(action_metadata.Q_source_state,
                            action_metadata.source_node_encoding,
                            after_toplevel_state,
                            reward,
                            self.gamma,
                            self.learning_rate)

        qattack_state_after = self.qattack.state_space.encode_at(
            agent_state, action_metadata.source_node)
        self.qattack.update(action_metadata.Q_attack_state,
                            int(action_metadata.abstract_action),
                            qattack_state_after,
                            reward,
                            self.gamma,
                            self.learning_rate)

    def end_of_iteration(self, t, done):
        """Reset."""
        self.loss_qsource.end_of_iteration(t, done)
        self.loss_qattack.end_of_iteration(t, done)

    def end_of_episode(self, i_episode, t):
        """Reset."""
        self.loss_qsource.end_of_episode(i_episode, t)
        self.loss_qattack.end_of_episode(i_episode, t)

    def new_episode(self):
        """Reset."""
        self.loss_qsource.new_episode()
        self.loss_qattack.new_episode()

    def exploit(self, wrapped_env, observation, log):
        """Return if possible a gym action exploiting both QMatrix."""
        agent_state = wrapped_env.state

        qsource_state = self.qsource.state_space.encode(agent_state)

        log, action_style, gym_action, _ = self.credcache_policy.exploit(
            wrapped_env, observation, log)

        if gym_action:
            source_node = sourcenode_of_action(gym_action)

            return log, action_style, gym_action, ChosenActionMetadata(Q_source_state=qsource_state, Q_source_expected=-1,
                                                                       Q_attack_expected=-1, source_node=source_node,
                                                                       source_node_encoding=self.qsource.action_space.encode_at(
                                                                           agent_state, source_node),
                                                                       abstract_action=self.qattack.action_space.abstract_from_gymaction(
                                                                           gym_action),
                                                                       Q_attack_state=self.qattack.state_space.encode_at(agent_state, source_node))

        action_style = 'exploit'
        source_node_encoding, qsource_expectedq = self.qsource.exploit(
            qsource_state, self.exploit_percentile)

        potential_source_nodes = [
            from_node for from_node in np.nonzero(
                observation.nodes_privilegelevel)[0] if source_node_encoding == self.qsource.action_space.encode_at(
                agent_state, from_node)]

        if len(potential_source_nodes) == 0:
            log += 'No node with encoding {}, fallback on explore\n'.format(
                source_node_encoding)

            self.qsource.update(
                qsource_state,
                source_node_encoding,
                qsource_state,
                reward=0,
                gamma=self.gamma,
                learning_rate=self.learning_rate)

            return log, "exploit-1->explore", None, None

        else:
            source_node = np.random.choice(potential_source_nodes)

            qattack_state = self.qattack.state_space.encode_at(
                agent_state, source_node)

            abstract_action, qattack_expectedq = self.qattack.exploit(
                qattack_state, self.exploit_percentile)

            log, gym_action = self.qattack.action_space.specialize_to_gymaction(
                source_node=source_node, observation=observation, abstract_action_index=abstract_action, log=log)

            assert int(abstract_action) < self.qattack.action_space.flat_size()

            if gym_action and wrapped_env.env.is_action_valid(
                    gym_action, observation.action_mask):
                log += 'exploit gym_action={} source_node_encoding={}\n'.format(
                    abstract_action, source_node_encoding)

                return log, action_style, gym_action, ChosenActionMetadata(Q_source_state=qsource_state,
                                                                           Q_source_expected=qsource_expectedq,
                                                                           Q_attack_expected=qattack_expectedq,
                                                                           source_node=source_node,
                                                                           source_node_encoding=source_node_encoding,
                                                                           abstract_action=abstract_action,
                                                                           Q_attack_state=qattack_state)

            else:

                self.qsource.update(
                    qsource_state,
                    source_node_encoding,
                    qattack_state,
                    reward=0,
                    gamma=self.gamma,
                    learning_rate=self.learning_rate)

                self.qattack.update(
                    qattack_state,
                    int(abstract_action),
                    qattack_state,
                    reward=0,
                    gamma=self.gamma,
                    learning_rate=self.learning_rate)

                return log, 'exploit[invalid]->explore' if gym_action else 'exploit[undefined]->explore', None, None

    def explore(self, wrapped_env):
        """Return a random valid action."""
        agent_state = wrapped_env.state
        gym_action = wrapped_env.env.sample_valid_action(kinds=[0, 1, 2])
        abstract_action = self.qattack.action_space.abstract_from_gymaction(
            gym_action)

        assert int(abstract_action) < self.qattack.action_space.flat_size()

        source_node = sourcenode_of_action(gym_action)

        return 'explore', gym_action, ChosenActionMetadata(Q_source_state=self.qsource.state_space.encode(agent_state),
                                                           Q_source_expected=-1,
                                                           Q_attack_expected=-1,
                                                           source_node=source_node,
                                                           source_node_encoding=self.qsource.action_space.encode_at(
                                                               agent_state, source_node),
                                                           abstract_action=abstract_action,
                                                           Q_attack_state=self.qattack.state_space.encode_at(agent_state, source_node))

    def parameters_as_string(self):
        """Return hyper parameters as string."""
        return "gamma = {},\n learning_rate = {}\n, Q% = {}\n".format(
            self.gamma, self.learning_rate, self.exploit_percentile)

    def loss_as_string(self):
        """Return losses as string."""
        return '[loss_source={}\n \
                loss_attack={}]'.format(
            self.loss_qsource.current_episode_loss(),
            self.loss_qattack.current_episode_loss())

    def get_model(self):
        """Return both QMatrix."""
        return QTL(self.qattack, self.qsource)
