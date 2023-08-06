"""DeepQlearner allow us to test a Qlearning and double Qlearning where the defaut model is a simple Feed Forward neural network.

The Qlearning is implemented following the paper : https://arxiv.org/pdf/1312.5602.pdf
and the double deep Qlearning following the paper : https://arxiv.org/pdf/1509.06461.pdf
"""

import numpy as np
import random

from keras import Model
import keras.backend as K
from keras.layers import Dense, Input, Lambda
from tensorflow.keras.optimizers import RMSprop
from keras.models import clone_model

from .utils.agent_wrapper import *
from .RandomCredLookUp import CredentialCacheExploiter
from ..utils.objects_and_global_functions import *


def mean_q(y_true, y_pred):
    """Compute the average of maximum reward values per prediction."""
    return K.mean(K.max(y_pred, axis=-1))


def huber_loss(y_true, y_pred):
    """Compute the huber loss."""
    return .5 * K.square(y_true - y_pred)


def clipped_masked_error(args_list):
    """args_list is a list of 3 elements : y_true, y_pred, mask.

    Compute the huber loss and apply mask before returning the loss sum.
    """
    y_true, y_pred, mask = args_list

    loss = huber_loss(y_true, y_pred)
    loss *= mask

    return K.sum(loss, axis=-1)


class ChosenActionMetada:
    """Track an action."""

    def __init__(self, abstract_action, actor_node,
                 actor_features, actor_state):
        """Track elements seen at t for pushing it at t + 1 after the next environment step."""
        self.abstract_action = abstract_action
        self.actor_node = actor_node
        self.actor_features = actor_features
        self.actor_state = actor_state


def defaut_model(input_dim, output_dim):
    """Return a FFNN where the input shape is (input_dim,) and output shape is (output_dim,)."""
    input = Input(shape=(input_dim,))
    x = Dense(1024)(input)
    x = Dense(512)(x)
    x = Dense(128)(x)
    output = Dense(output_dim, activation=None)(x)

    return Model(input, output)


class Experiences:
    """Experiences allowing to build the dataset to train the model."""

    def __init__(self, state0, action, reward, state1):
        """Combine state0 and reward which are seen at t, action which is decided at t and state1 which is the next state at t + 1."""
        self.state0 = state0
        self.state1 = state1
        self.action = action
        self.reward = reward


class ReplayMemory(object):
    """Dataset to train the model."""

    def __init__(self, capacity):
        """Set the memory capacity."""
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, current_state, action, next_state, reward):
        """Push an experience into the memory."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)

        self.memory[self.position] = Experiences(
            state0=current_state.tolist(), action=action, reward=reward,
            state1=next_state.tolist() if isinstance(
                next_state, np.ndarray) else next_state
        )
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        """Return a batch of size batch_size of the memory."""
        return random.sample(self.memory, batch_size)

    def length(self):
        """Get the memory length."""
        return self.position

    def reset(self):
        """Empty memory."""
        self.memory = []
        self.position = 0


class CyberBattleStateActionModel:
    """Implement chosen action."""

    def __init__(self, env_bounds):
        """Merge needed features to set up action and state spaces."""
        self.env_bounds = env_bounds

        self.global_features = ConcatFeatures(
            env_bounds, [
                Feature_discovered_notowned_node_count(
                    env_bounds, clip=None)])

        self.node_specific_features = ConcatFeatures(env_bounds, [
            Feature_succes_actions_at_node(env_bounds),
            Feature_failed_actions_at_node(env_bounds),
            Feature_active_node_properties(env_bounds),
            Feature_active_node_age(env_bounds)
        ])

        self.state_space = ConcatFeatures(
            env_bounds,
            self.global_features.feature_selection +
            self.node_specific_features.feature_selection)

        self.action_space = AbstractAction(env_bounds)

    def implement_action(self, wrapped_env, actor_features,
                         abstract_action, log):
        """Implement chosen action.

        Agent will chose an abstract action (int). This function chose randomly a node as a source for this attack.
        """
        observation = wrapped_env.state.observation

        owned_nodes = np.nonzero(observation.nodes_privilegelevel)[0]

        potential_source_nodes = []

        for from_node in owned_nodes:

            if np.all(actor_features == self.node_specific_features.get(
                    wrapped_env.state, from_node)):

                potential_source_nodes.append(from_node)

        if len(potential_source_nodes) > 0:

            source_node = np.random.choice(potential_source_nodes)

            log, gym_action = self.action_space.specialize_to_gymaction(
                source_node, observation, abstract_action, log)

            if not gym_action:
                return log, "exploit[undefined]->explore", None, None

            elif wrapped_env.env.is_action_valid(gym_action, observation.action_mask):
                return log, "exploit", gym_action, source_node

            else:
                return log, "exploit[invalid]->explore", None, None

        else:
            return log, "exploit[no_actor]->explore", None, None


class DeepQlearner:
    """The core class."""

    def __init__(self, env_bounds, gamma,
                 replay_memory_size, target_update, batch_size, learning_rate,
                 agent_model=None, enable_double_dqn=False, tau=0.08
                 ):
        """Initialize every hyper parameters and the target and trainable model."""
        # hyper parameters
        self.states = CyberBattleStateActionModel(env_bounds)
        self.enable_double_dqn = enable_double_dqn
        self.batch_size = batch_size
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.memory = ReplayMemory(capacity=replay_memory_size)
        self.replay_memory_size = replay_memory_size
        self.target_update = target_update
        self.step = 0
        self.tau = tau

        self.credcache_policy = CredentialCacheExploiter()

        self.input_dim = len(self.states.state_space.dim_sizes)
        self.output_dim = self.states.action_space.flat_size()
        optimizer = RMSprop(learning_rate=learning_rate)

        # target model
        if agent_model:
            self.model = agent_model

        else:
            self.model = defaut_model(self.input_dim, self.output_dim)

        self.target_model = clone_model(self.model)

        self.model.compile(optimizer=optimizer, loss='mse')
        self.target_model.compile(optimizer=optimizer, loss='mse')

        # trainable model
        y_pred = self.target_model.output
        y_true = Input(name='y_true', shape=(self.output_dim,))
        mask = Input(name='mask', shape=(self.output_dim,))
        loss_out = Lambda(clipped_masked_error, output_shape=(
            1,), name='loss')([y_true, y_pred, mask])
        ins = [self.target_model.input] if not isinstance(
            self.target_model.input, list) else self.target_model.input

        self.trainable_model = Model(inputs=ins +
                                     [y_true, mask], outputs=[loss_out, y_pred])

        assert len(self.trainable_model.output_names) == 2

        combined_metrics = {self.trainable_model.output_names[1]: mean_q}
        losses = [
            lambda y_true, y_pred: y_pred,
            lambda y_true, y_pred: K.zeros_like(y_pred)
        ]

        self.trainable_model.compile(
            optimizer=optimizer,
            loss=losses,
            metrics=combined_metrics)

    def parameters_as_string(self):
        """Return hyper parameters as string."""
        return "γ={}, lr={}, replaymemory={}, batch={}, target_update={}".format(
            self.gamma,
            self.learning_rate,
            self.replay_memory_size,
            self.batch_size,
            self.target_update)

    def all_parameters_as_string(self):
        """Return hyper parameters as string and input and output dimension of the model."""
        return "{}\ndimension={}x{}, Q={} -> abstract_action".format(
            self.parameters_as_string(), self.states.state_space.flat_size(), self.states.action_space.flat_size(), [
                f.name() for f in self.states.state_space.feature_selection])

    def get_actor_state_vector(self, global_state, actor_features):
        """Concatenante specifics and global features."""
        return np.concatenate([global_state, actor_features])

    def optimize_model(self):
        """Prepare a batch of data for training and do one backpropagation with it accross the trainable model following papers methods."""
        if self.memory.length() < self.batch_size:
            return

        # dataset
        experiences = self.memory.sample(self.batch_size)

        assert len(experiences) == self.batch_size

        state0_batch = []
        terminal_batch = []
        reward_batch = []
        action_batch = []
        state1_batch = []
        for e in experiences:
            state0_batch.append(e.state0)
            state1_batch.append(
                e.state1 if isinstance(
                    e.state1,
                    list) else [0] *
                self.input_dim)
            terminal_batch.append(1. if e.state1 else 0.)
            reward_batch.append(e.reward)
            action_batch.append(e.action)

        terminal_batch = np.array(terminal_batch)
        state0_batch = np.array(state0_batch)
        state1_batch = np.array(state1_batch)
        reward_batch = np.array(reward_batch)
        action_batch = np.array(action_batch)

        assert reward_batch.shape == (self.batch_size,)
        assert action_batch.shape[0] == reward_batch.shape[0]

        # forward
        if self.enable_double_dqn:

            q_values = self.model.predict_on_batch(state1_batch)
            assert q_values.shape == (self.batch_size, self.output_dim)
            actions = np.argmax(q_values, axis=1)
            assert actions.shape == (self.batch_size,)

            target_q_values = self.target_model.predict_on_batch(state1_batch)
            assert target_q_values.shape == (self.batch_size, self.output_dim)
            q_batch = np.zeros(self.batch_size)
            for i, a in enumerate(actions):
                q_batch[i] = target_q_values[i, a]

        else:

            target_q_values = self.target_model.predict_on_batch(state1_batch)
            assert target_q_values.shape == (self.batch_size, self.output_dim)
            q_batch = np.max(target_q_values, axis=1).flatten()

        # backward
        targets = np.zeros((self.batch_size, self.output_dim))
        dummy_targets = np.zeros((self.batch_size,))
        masks = np.zeros((self.batch_size, self.output_dim))

        discounted_reward_batch = self.gamma * q_batch
        discounted_reward_batch *= terminal_batch

        assert discounted_reward_batch.shape == reward_batch.shape

        Rs = reward_batch + discounted_reward_batch
        for idx, (target, mask, R, action) in enumerate(
                zip(targets, masks, Rs, action_batch)):
            target[action] = R
            dummy_targets[idx] = R
            mask[action] = 1.

        ins = [state0_batch] if not isinstance(
            self.model.input, list) else state0_batch
        self.trainable_model.train_on_batch(
            x=ins + [targets, masks], y=[dummy_targets, targets])

        # update target_model's weights
        if self.step % self.target_update == 0:
            self.target_model.set_weights(self.trainable_model.get_weights())

            if self.enable_double_dqn:

                teta = self.target_model.get_weights()
                teta_p = self.model.get_weights()
                new_weights = []
                for t, t_p in zip(teta, teta_p):
                    new_weights.append(self.tau * t_p + (1 - self.tau) * t)
                self.model.set_weights(new_weights)

    def update_q_function(self, reward, actor_state,
                          abstract_action, next_actor_state=None):
        """Fill the memory with environment step experience and optimize the model."""
        self.memory.push(
            actor_state,
            abstract_action,
            next_actor_state,
            reward)
        self.optimize_model()

    def on_step(self, wrapped_env, observation,
                reward, done, info, action_metada):
        """Fill with a non terminal experience if the epoch isn't finish."""
        self.step += 1

        agent_state = wrapped_env.state
        if done:
            self.update_q_function(
                reward,
                actor_state=action_metada.actor_state,
                abstract_action=action_metada.abstract_action,
                next_actor_state=None)

        else:
            next_global_state = self.states.global_features.get(
                agent_state, node=None)
            next_actor_features = self.states.node_specific_features.get(
                agent_state, action_metada.actor_node)
            next_actor_state = self.get_actor_state_vector(
                next_global_state, next_actor_features)

            self.update_q_function(
                reward,
                actor_state=action_metada.actor_state,
                abstract_action=action_metada.abstract_action,
                next_actor_state=next_actor_state)

    def end_of_episode(self, i_episode, t):
        """Reset the iteration count."""
        self.step = 0

    def metadata_from_gym_action(self, wrapped_env, gym_action):
        """Set the ChosenActionMetada of iteration t providing the wrapped environment and gym action."""
        current_global_state = self.states.global_features.get(
            wrapped_env.state, node=None)
        actor_node = sourcenode_of_action(gym_action)
        actor_features = self.states.node_specific_features.get(
            wrapped_env.state, actor_node)
        abstract_action = self.states.action_space.abstract_from_gymaction(
            gym_action)

        return ChosenActionMetada(
            abstract_action=abstract_action,
            actor_node=actor_node,
            actor_features=actor_features,
            actor_state=self.get_actor_state_vector(
                current_global_state,
                actor_features))

    def explore(self, wrapped_env):
        """Return a random valid action."""
        gym_action = wrapped_env.env.sample_valid_action(kinds=[0, 1, 2])
        meta_data = self.metadata_from_gym_action(wrapped_env, gym_action)

        return "explore", gym_action, meta_data

    def try_exploit_at_candidate_actor_states(
            self,
            wrapped_env,
            current_global_state,
            actor_features,
            abstract_action,
            log):
        """Exploit a provided abstract action.

        If it failed, the function fill the memory with a null reward.
        """
        actor_state = self.get_actor_state_vector(
            current_global_state, actor_features)
        log, action_style, gym_action, actor_node = self.states.implement_action(
            wrapped_env, actor_features, abstract_action, log)

        if gym_action:
            assert actor_node is not None, 'actor_node should be set together with {}'.format(
                gym_action)

            return log, action_style, gym_action, ChosenActionMetada(
                abstract_action=abstract_action,
                actor_node=actor_node,
                actor_features=actor_features,
                actor_state=actor_state
            )

        else:

            self.update_q_function(reward=0.0,
                                   actor_state=actor_state,
                                   next_actor_state=actor_state,
                                   abstract_action=abstract_action)

            return log, "exploit[undefined]->explore", None, None

    def lookup(self, states_to_consider):
        """Forward pass."""
        output = self.target_model.predict(states_to_consider)
        action_lookups = np.argmax(output, axis=1).tolist()
        expectedq_lookups = np.max(output, axis=1).tolist()

        return action_lookups, expectedq_lookups

    def exploit(self, wrapped_env, observation, log):
        """Try first to exploit a credential.

        If it's impossible, forward to the model each features vector where specific features are computed on owned nodes.
        """
        log, action_style, gym_action, _ = self.credcache_policy.exploit(
            wrapped_env, observation, log)

        if gym_action:
            return log, action_style, gym_action, self.metadata_from_gym_action(
                wrapped_env, gym_action)

        current_global_state = self.states.global_features.get(
            wrapped_env.state, node=None)

        owned_nodes = np.nonzero(observation.nodes_privilegelevel)[0]

        active_actors_features = []

        for from_node in owned_nodes:
            active_actors_features.append(
                self.states.node_specific_features.get(
                    wrapped_env.state, from_node))

        unique_active_actors_features = np.unique(
            active_actors_features, axis=0)

        candidate_actor_state_vector = []

        for node_features in unique_active_actors_features:

            candidate_actor_state_vector.append(
                self.get_actor_state_vector(
                    current_global_state, node_features))

        candidate_actor_state_vector_length = len(candidate_actor_state_vector)
        candidate_actor_state_vector = np.vstack(candidate_actor_state_vector)

        remaining_action_lookups, remaining_expectedq_lookups = self.lookup(
            candidate_actor_state_vector)
        remaining_candidate_indices = list(
            range(candidate_actor_state_vector_length))

        while remaining_candidate_indices:

            _, remaining_candidate_index = random_argmax(
                remaining_expectedq_lookups)
            actor_index = remaining_candidate_indices[remaining_candidate_index]
            abstract_action = remaining_action_lookups[remaining_candidate_index]
            actor_features = unique_active_actors_features[actor_index]

            log, action_style, gym_action, meta_data = self.try_exploit_at_candidate_actor_states(
                wrapped_env, current_global_state, actor_features, abstract_action, log)

            if gym_action:
                return log, action_style, gym_action, meta_data

            remaining_action_lookups.pop(remaining_candidate_index)
            remaining_expectedq_lookups.pop(remaining_candidate_index)
            remaining_candidate_indices.pop(remaining_candidate_index)

        return log, "exploit[undefined]->explore", None, None

    def get_model(self):
        """Return the target model."""
        return self.target_model
