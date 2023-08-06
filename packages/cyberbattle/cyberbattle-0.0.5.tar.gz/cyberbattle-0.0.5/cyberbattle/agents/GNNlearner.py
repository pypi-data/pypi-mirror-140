"""GNNlearner provides a learner class with an agent able to observe the full discovered network.

Furthermore, it is allowed to make its own encoding nodes in a specified latent space
and make a distribution regression on this lsit of encoded vector. Besides, these vectors
measures the nodes features and its contribution in the discovered network.
"""

import numpy as np
import random
import tensorflow as tf

from keras import Model, Sequential
import keras.backend as K
from tensorflow.keras.optimizers import RMSprop
from keras.layers import Layer, Dense, GRU, Lambda, Add, Flatten

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


def create_ffnn(hidden_unit):
    """Create a FFNN, auxiliary function.

    inputs : hidden_unit (int).
    Return a FFNN.
    """
    fnn = Sequential()
    fnn.add(Dense(512, activation=tf.nn.gelu))
    fnn.add(Dense(128, activation=tf.nn.gelu))
    fnn.add(Dense(hidden_unit))

    return fnn


class GraphLayer(Layer):
    """Build a layer able to build the node embeddings."""

    def __init__(
        self,
        max_node_count,
        hidden_units,
        num_step=1,
        dropout_rate=0.0,
        combination_type="gru",
        normalize=False,
        num_GRU=1,
        *args,
        **kwargs
    ):
        """Init parameters.

        num_step correspond to how deep we check the node contribution in the network.
        hidden_units indicate the latent space dimension to encode our nodes.
        """
        super().__init__(*args, **kwargs)

        assert num_step > 0

        self.combination_type = combination_type
        self.normalize = normalize
        self.num_step = num_step
        self.hidden_units = hidden_units
        self.num_GRU = num_GRU
        self.max_node_count = max_node_count

        self.ffnn_prepare = create_ffnn(hidden_units)

        if self.combination_type == 'gru':
            if num_GRU:
                self.update_layers = []

                for _ in range(num_GRU):

                    self.update_layers.append(GRU(
                        units=hidden_units,
                        dropout=dropout_rate,
                        return_state=True,
                        recurrent_dropout=dropout_rate
                    ))

            else:

                self.update_layer = GRU(
                    units=hidden_units,
                    dropout=dropout_rate,
                    return_state=True,
                    recurrent_dropout=dropout_rate
                )

        else:
            self.update_layer = create_ffnn(hidden_units)

    def aggregate(self, node_representations, weights, use_ffnn=False):
        """node_representations shape is (maximum_node_count, embedding_dim), weights shape is (maximum_node_count, maximum_node_count).

        Return a embedded node_representations gathering flows accross
        the graph of shape (maximum_node_count, hidden_units).
        """
        if use_ffnn:

            node_embeddings = self.ffnn_prepare(node_representations)

            return tf.matmul(weights, node_embeddings), node_embeddings

        else:

            return tf.matmul(weights, node_representations)

    def update(self, node_representations, aggregated_messages):
        """Input : node_representations shape is (maximum_node_count, hidden_units), aggregated_messages shape is (maximum_node_count, aggregated_units).

        Return node_embeddings of shape (maximum_node_count, hidden_units).
        """
        if self.combination_type == 'gru':

            num_nodes = node_representations.shape[1]
            batch_size = node_representations.shape[0]

            node_representations_ = tf.reshape(
                node_representations, shape=(
                    batch_size * num_nodes, self.hidden_units, 1))
            aggregated_messages_ = tf.reshape(
                aggregated_messages, shape=(
                    batch_size * num_nodes, self.hidden_units))

            for i in range(self.num_GRU):

                layer = self.update_layers[i]
                node_representations_, aggregated_messages_ = layer(
                    node_representations_, initial_state=aggregated_messages_)
                node_representations_ = tf.expand_dims(
                    node_representations_, axis=-1)

            return tf.reshape(node_representations_, shape=(
                batch_size, num_nodes, self.hidden_units))

        else:

            if self.combination_type == 'concat':
                h = tf.concat(
                    [node_representations, aggregated_messages], axis=2)

            elif self.combination_type == 'add':
                h = node_representations + aggregated_messages

            else:
                raise ValueError(
                    f"Invalid combination type: {self.combination_type}.")

            node_embeddings = self.update_layer(h)

            if self.normalize:
                node_embeddings = tf.nn.l2_normalize(node_embeddings, axis=-1)

            return node_embeddings

    def call(self, inputs):
        """Input is an array of shape (maximum_node_count, maximum_node_count + maximum_property_count + maximum_total_credential + 3).

        Return node_embeddings of shape (maximum_node_count, representation_dim).
        """
        edge_weights = inputs[:, :, :self.max_node_count]
        node_representations = inputs[:, :, self.max_node_count:]

        aggregated_messages, node_embeddings = self.aggregate(
            node_representations, edge_weights, use_ffnn=True)
        node_embeddings = self.update(node_embeddings, aggregated_messages)

        for _ in range(self.num_step - 1):

            aggregated_messages = self.aggregate(node_embeddings, edge_weights)
            node_embeddings = self.update(node_embeddings, aggregated_messages)

        return node_embeddings


class Defaut_GNN_model(Model):
    """A GNN model."""

    def __init__(self, hidden_units, max_node_count, output_dim,
                 combination_type, num_step=1, num_GRU=1):
        """Init layers."""
        super().__init__()

        self._jit_compile = None
        self.graphlayer = GraphLayer(
            max_node_count=max_node_count,
            hidden_units=hidden_units,
            num_step=num_step,
            num_GRU=num_GRU,
            combination_type=combination_type)
        self.linear_1 = Dense(512)
        self.linear_2 = Dense(1024)
        self.linear_3 = Dense(512)
        self.linear_4 = Dense(512)
        self.linear_5 = Dense(256)
        self.linear_6 = Dense(output_dim)

    def call(self, inputs):
        """Input is a list of 2 array of shape (num_nodes, num_nodes + nb_features) and (node_features_dim,).

        Return an array of shape (nb_action,) which represents estimated rewards using the node as source.
        """
        graph, node_features = inputs
        x1 = self.graphlayer(graph)
        x1 = Flatten()(x1)
        encoded_graph = self.linear_1(x1)

        x2 = self.linear_2(node_features)
        x2 = self.linear_3(x2)

        x = Add()([encoded_graph, x2])
        x = self.linear_4(x)
        x = self.linear_5(x)

        return self.linear_6(x)


class trainable_model(Model):
    """Model to update at each iterations."""

    def __init__(self, tracked_model):
        """Init the model to track."""
        super().__init__(self)

        self.tracked_model = tracked_model

    def call(self, inputs):
        """Input is a list of 3 elements : an input for the tracked_model, y_true, mask.

        Return the loss out and the tracked_model prediction.
        """
        ins, y_true, mask = inputs
        y_pred = self.tracked_model(ins)
        loss_out = Lambda(clipped_masked_error, output_shape=(
            1,), name='loss')([y_true, y_pred, mask])

        return loss_out, y_pred


class ActionGNN:
    """Class to implement the chosen action by the GNN agant."""

    def __init__(self, env_bounds):
        """Init action space."""
        self.action_space = AbstractAction(env_bounds)

        self.graph = HstackFeature(env_bounds, [
            # very important to first set adjacent matrix for the GNN model
            Feature_weights(env_bounds),
            Feature_active_properties(env_bounds),
            # Feature_discovered_credentials(env_bounds),
            Feature_privilegelevel(env_bounds),
            Feature_succes_actions(env_bounds),
            Feature_failed_actions(env_bounds)
        ])
        self.node_features = ConcatFeatures(env_bounds, [
            Feature_succes_actions_at_node(env_bounds),
            Feature_failed_actions_at_node(env_bounds),
            Feature_active_node_properties(env_bounds),
            Feature_active_node_age(env_bounds)
        ])

    def implement_action(
            self,
            wrapped_env,
            abstract_action,
            node_feature,
            log):
        """Return a gym action and the chosen source node."""
        observation = wrapped_env.state.observation

        owned_nodes = np.nonzero(observation.nodes_privilegelevel)[0]

        potential_source_nodes = []

        for from_node in owned_nodes:

            if np.all(node_feature == self.node_features.get(
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


class ChosenActionMetada:
    """Track an action."""

    def __init__(
            self,
            abstract_action,
            graph,
            source_node_feature,
            source_node_id):
        """Track elements seen at t for pushing it at t + 1 after the next environment step."""
        self.abstract_action = abstract_action
        self.source_node_feature = source_node_feature
        self.source_node_id = source_node_id
        self.graph = graph


class Experience:
    """Experiences allowing to build the dataset to train the model."""

    def __init__(self, graph0, action, reward, graph1, source0, source1):
        """Combine graph0 and reward which are seen at t, action which is decided at t and graph1 which is the next state at t + 1."""
        self.graph0 = graph0
        self.graph1 = graph1
        self.action = action
        self.reward = reward
        self.source0 = source0
        self.source1 = source1


class ReplayMemory(object):
    """Dataset to train the model."""

    def __init__(self, capacity):
        """Set the memory capacity."""
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(
            self,
            current_graph,
            action,
            next_graph,
            reward,
            source_node_feature,
            next_source_node_feature):
        """Push an experience into the memory."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)

        self.memory[self.position] = Experience(
            graph0=current_graph,
            action=action,
            reward=reward,
            graph1=next_graph,
            source0=source_node_feature,
            source1=next_source_node_feature
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


class GNNlearner:
    """The core class."""

    def __init__(self,
                 env_bounds,
                 gamma,
                 embedding_space_dimension,
                 replay_memory_size,
                 learning_rate,
                 target_update,
                 batch_size,
                 combination_type='gru',
                 num_step=2,
                 num_GRU=1,
                 agent_model=None
                 ):
        """Init hyper parameters.

        Init trainable target model too.
        """
        # hyper params
        self.env_bounds = env_bounds
        self.action = ActionGNN(env_bounds)
        self.embedding_space_dimension = embedding_space_dimension
        self.gamma = gamma
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.target_update = target_update
        self.replay_memory_size = replay_memory_size
        self.step = 0
        self.credcache_policy = CredentialCacheExploiter()
        self.memory = ReplayMemory(replay_memory_size)
        self.optimizer = RMSprop(learning_rate=self.learning_rate)

        self.node_features_dim = len(self.action.node_features.dim_sizes)
        self.discovered_graph_shape = (int(self.env_bounds.maximum_node_count), int(
            len(self.action.graph.dim_sizes) / self.env_bounds.maximum_node_count))
        self.output_dim = self.action.action_space.flat_size()
        # target model
        if agent_model:
            self.target_model = agent_model

        else:
            self.target_model = Defaut_GNN_model(
                max_node_count=self.env_bounds.maximum_node_count,
                hidden_units=self.embedding_space_dimension,
                num_step=num_step,
                num_GRU=num_GRU,
                combination_type=combination_type,
                output_dim=self.output_dim
            )

            self.target_model.compile(optimizer=self.optimizer, loss='mse')

        # trainable model
        self.trainable_model = trainable_model(tracked_model=self.target_model)

        combined_metrics = {'output_2': mean_q}
        losses = [
            lambda y_true, y_pred: y_pred,
            lambda y_true, y_pred: K.zeros_like(y_pred)
        ]

        self.trainable_model.compile(
            optimizer=self.optimizer,
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

    def optimize_model(self):
        """Prepare a batch of data for training and do one backpropagation with it accross the trainable GNN model following papers methods."""
        if self.memory.length() < self.batch_size:
            return

        # dataset
        experiences = self.memory.sample(self.batch_size)
        graph_shape = (self.batch_size,) + self.discovered_graph_shape

        graph0_batch = np.zeros(graph_shape,
                                dtype=float)
        graph1_batch = np.zeros(graph_shape,
                                dtype=float)
        node_features0_batch = np.zeros(
            (self.batch_size, self.node_features_dim))
        node_features1_batch = np.zeros(
            (self.batch_size, self.node_features_dim))
        reward_batch = np.zeros((self.batch_size,), dtype=float)
        action_batch = np.zeros((self.batch_size,), dtype=int)
        for i, e in enumerate(experiences):

            graph0_batch[i] = e.graph0
            graph1_batch[i] = e.graph1
            reward_batch[i] = e.reward
            action_batch[i] = e.action
            node_features0_batch[i] = e.source0
            node_features1_batch[i] = e.source1

        is_terminal_batch = np.where(
            np.count_nonzero(graph1_batch) == 0, 0., 1.0)

        target_q_values = self.target_model(
            [graph1_batch, node_features1_batch])
        q_batch_max = np.max(target_q_values, axis=-1)

        targets = np.zeros(
            (self.batch_size,
             self.output_dim))
        masks = np.zeros(
            (self.batch_size,
             self.output_dim))
        dummy_targets = np.zeros((self.batch_size,))

        discounted_reward = self.gamma * q_batch_max * is_terminal_batch

        Rs = reward_batch + discounted_reward
        for idx, (target, mask, R, action) in enumerate(
                zip(targets, masks, Rs, action_batch)):
            target[action] = R
            dummy_targets[idx] = R
            mask[action] = 1.

        # forward and backward
        self.trainable_model.train_on_batch(
            x=[[graph0_batch, node_features0_batch], targets, masks], y=[dummy_targets, targets])

        if self.step % self.target_update == 0:
            self.target_model.set_weights(self.trainable_model.get_weights())

    def update_q_function(self,
                          reward,
                          current_graph,
                          abstract_action,
                          source_node,
                          next_node,
                          next_graph
                          ):
        """Fill the memory with environment step experience and optimize the model."""
        self.memory.push(
            current_graph=current_graph,
            action=abstract_action,
            source_node_feature=source_node,
            next_graph=next_graph,
            next_source_node_feature=next_node,
            reward=reward
        )
        self.optimize_model()

    def explore(self, wrapped_env):
        """Return a random valid action."""
        gym_action = wrapped_env.env.sample_valid_action(kinds=[0, 1, 2])
        meta_data = self.metadata_from_gym_action(wrapped_env, gym_action)

        return "explore", gym_action, meta_data

    def on_step(self, wrapped_env, observation,
                reward, done, info, action_metada):
        """Fill with a non terminal experience if the epoch isn't finish."""
        self.step += 1

        state = wrapped_env.state
        source_node_feature = action_metada.source_node_feature
        if done:
            self.update_q_function(
                reward=reward,
                current_graph=action_metada.graph,
                abstract_action=action_metada.abstract_action,
                source_node=source_node_feature,
                next_node=np.zeros(self.node_features_dim),
                next_graph=np.zeros(self.discovered_graph_shape)
            )

        else:
            next_source_feature = self.action.node_features.get(
                state, node=action_metada.source_node_id)
            next_graph = self.action.graph.get(state, node=None)
            self.update_q_function(
                reward=reward,
                current_graph=action_metada.graph,
                abstract_action=action_metada.abstract_action,
                source_node=source_node_feature,
                next_node=next_source_feature,
                next_graph=next_graph
            )

    def metadata_from_gym_action(self, wrapped_env, gym_action):
        """Set the Chosen ActionMetada of iteration t providing the wrapped environment and gym action."""
        state = wrapped_env.state
        current_graph = self.action.graph.get(state, node=None)
        abstract_action = self.action.action_space.abstract_from_gymaction(
            gym_action)
        source_node = sourcenode_of_action(gym_action)
        source_node_feature = self.action.node_features.get(
            state, node=source_node)

        return ChosenActionMetada(
            abstract_action=abstract_action,
            graph=current_graph,
            source_node_id=source_node,
            source_node_feature=source_node_feature
        )

    def lookup(self, graph, source_node_feature):
        """Forward pass through Regressor model."""
        output = self.target_model(
            [graph, source_node_feature])
        abstract_action_lookup = np.argmax(output, axis=-1)
        expectedq_lookup = np.max(output, axis=-1)

        return abstract_action_lookup, expectedq_lookup

    def try_exploit_at_source_node(
            self,
            wrapped_env,
            current_graph,
            abstract_action,
            source_node_feature,
            log):
        """Exploit a provided abstract action.

        If it failed, the function fill the memory with a null reward.
        """
        log, action_style, gym_action, source_node = self.action.implement_action(
            wrapped_env, abstract_action, source_node_feature, log)

        if gym_action:
            assert source_node is not None, 'source_node should be set together with {}'.format(
                gym_action)

            return log, action_style, gym_action, ChosenActionMetada(
                abstract_action=abstract_action,
                graph=current_graph,
                source_node_feature=source_node_feature,
                source_node_id=source_node
            )

        else:

            self.update_q_function(
                reward=0.0,
                current_graph=current_graph,
                abstract_action=abstract_action,
                source_node=source_node_feature,
                next_node=np.zeros(
                    self.node_features_dim),
                next_graph=np.zeros(self.discovered_graph_shape)
            )

            return log, "exploit[undefined]->explore", None, None

    def exploit(self, wrapped_env, observation, log):
        """Try first to exploit a credential.

        If it's impossible, forward to the model the current graph and try to exploit the suggested action.
        """
        log, action_style, gym_action, _ = self.credcache_policy.exploit(
            wrapped_env, observation, log)

        if gym_action:
            return log, action_style, gym_action, self.metadata_from_gym_action(
                wrapped_env, gym_action)

        state = wrapped_env.state
        current_graph = self.action.graph.get(state, node=None)
        graph_shape = current_graph.shape
        owned_nodes = np.nonzero(observation.nodes_privilegelevel)[0]

        graphs = np.zeros(
            (owned_nodes.shape[0],
             graph_shape[0],
             graph_shape[1]))
        for i in range(owned_nodes.shape[0]):
            graphs[i, :, :] = current_graph

        active_actors_features = []

        for from_node in owned_nodes:
            active_actors_features.append(
                self.action.node_features.get(
                    wrapped_env.state, from_node))

        candidate_actor_state_vector_length = len(active_actors_features)
        candidate_actor_state_vector = np.vstack(active_actors_features)

        remaining_action_lookups, remaining_expectedq_lookups = self.lookup(
            graph=graphs, source_node_feature=candidate_actor_state_vector)

        remaining_action_lookups = remaining_action_lookups.tolist()
        remaining_expectedq_lookups = remaining_expectedq_lookups.tolist()
        remaining_candidate_indices = list(
            range(candidate_actor_state_vector_length))

        while remaining_candidate_indices:

            remaining_candidate_index = np.argmax(remaining_expectedq_lookups)

            actor_index = remaining_candidate_indices[remaining_candidate_index]
            abstract_action = remaining_action_lookups[remaining_candidate_index]
            actor_features = active_actors_features[actor_index]

            log, action_style, gym_action, meta_data = self.try_exploit_at_source_node(
                wrapped_env=wrapped_env,
                current_graph=current_graph,
                abstract_action=abstract_action,
                source_node_feature=actor_features,
                log=log
            )

            if gym_action:
                return log, action_style, gym_action, meta_data

            remaining_action_lookups.pop(remaining_candidate_index)
            remaining_expectedq_lookups.pop(remaining_candidate_index)
            remaining_candidate_indices.pop(remaining_candidate_index)

        return log, "exploit[undefined]->explore", None, None

    def end_of_episode(self, i_episode, t):
        """Reset step number."""
        self.step = 0

    def get_model(self):
        """Return the target model."""
        return self.target_GNN_model, self.target_Regressor_model
