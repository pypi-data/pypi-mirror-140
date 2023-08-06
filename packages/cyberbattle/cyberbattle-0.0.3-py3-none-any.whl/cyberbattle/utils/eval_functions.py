"""Provide a function allowing us to train and test agents on different environments."""

import gym
import matplotlib.pyplot as plt

from env_processing import register_env
from ..agents.utils.agent_policy import epsilon_greedy_search, run_random_agent
from ..utils.objects_and_global_functions import *
from ..agents.utils.plot import plot_episodes_rewards_averaged, plot_episodes_availability_averaged, plot_episodes_length

from ..agents.DeepQlearner import DeepQlearner
from ..agents.GNNlearner import GNNlearner
from ..agents.Qlearner import QTabularLearner
from ..agents.RandomCredLookUp import CredentialCacheExploiter

register_env()


def envs_generation(args):
    """List of string of wished environment to generate."""
    return [gym.make(i) for i in args]


def bounds(envs):
    """Return an overestimated number of node and credentials in the network."""
    return [EnvironmentBounds.of_identifiers(
        identifiers=env._CyberBattleEnv__initial_environment.identifiers,
        maximum_node_count=env._CyberBattleEnv__node_count,
        maximum_total_credentials=22
    )
        for env in envs]


def train_and_eval_agents(
        environment_names,
        iteration_count=5000,
        training_episode_count=250,
        gamma=0.15,
        replay_memory_size=10000,
        embedding_space_dimension=64,
        num_step=1,
        num_GRU=2,
        batch_size=512,
        target_update=5,
        learning_rate=0.01,
        epsilon=0.9,
        epsilon_minimum=0.001,
        epsilon_exponential_decay=5000,
        render=None,
        random_agent=True,
        plot=False,
        display_stats=False,
        plot_method='agentsTOenvs'
):
    """Train all agents for each provided environment and plot the evaluation of each agents in each all provided environment."""
    envs = envs_generation(environment_names)
    env_bounds = bounds(envs)
    _agent_names = [
        "DQL",
        "DDQL",
        "QTL",
        "GNN_concat",
        "GNN_GRU",
        "RandomCredentialLookUp",
        "RandomAgent"]

    if plot_method not in ['agentsTOenvs', 'envsTOagents']:
        return ValueError('UNKNOW ploting method : {}'.format(plot_method))

    if plot_method == 'agentsTOenvs':

        for i, cyber_env_battle in enumerate(envs):

            _agents = [
                DeepQlearner(
                    env_bounds=env_bounds[i],
                    gamma=gamma,
                    replay_memory_size=replay_memory_size,
                    target_update=target_update,
                    batch_size=batch_size,
                    learning_rate=learning_rate),
                DeepQlearner(
                    env_bounds=env_bounds[i],
                    gamma=gamma,
                    replay_memory_size=replay_memory_size,
                    target_update=target_update,
                    batch_size=batch_size,
                    learning_rate=learning_rate,
                    enable_double_dqn=True),
                QTabularLearner(
                    env_bounds=env_bounds[i],
                    gamma=gamma,
                    learning_rate=learning_rate),
                GNNlearner(
                    env_bounds=env_bounds[i],
                    gamma=gamma,
                    embedding_space_dimension=embedding_space_dimension,
                    replay_memory_size=replay_memory_size,
                    learning_rate=learning_rate,
                    target_update=target_update,
                    batch_size=batch_size,
                    combination_type='concat',
                    num_step=num_step),
                GNNlearner(
                    env_bounds=env_bounds[i],
                    gamma=gamma,
                    embedding_space_dimension=embedding_space_dimension,
                    replay_memory_size=replay_memory_size,
                    learning_rate=learning_rate,
                    target_update=target_update,
                    batch_size=batch_size,
                    combination_type='gru',
                    num_GRU=num_GRU,
                    num_step=num_step)]

            fig, axs = plt.subplots(3, figsize=(8, 20))
            fig.suptitle(f'Environment : {environment_names[i][:-3]}')
            axs[0].set_title(f"Cumulative rewards")
            axs[0].set(xlabel='Iteration', ylabel='Reward')
            axs[1].set_title(f"Network availabilities")
            axs[1].set(xlabel='Iteration', ylabel='Availability')
            axs[2].set_title(f"Length of each episode")
            axs[2].set(xlabel='epoch', ylabel='Iterations number')

            for _agent_name, _agent in zip(_agent_names, _agents):

                learner, _, _, _, _, train_durations = epsilon_greedy_search(
                    cyberbattle_env=cyber_env_battle,
                    env_bounds=env_bounds[i],
                    learner=_agent,
                    episode_count=training_episode_count,
                    iteration_count=iteration_count,
                    epsilon=epsilon,
                    epsilon_minimum=epsilon_minimum,
                    epsilon_exponential_decay=epsilon_exponential_decay,
                    title=_agent_name,
                    display_stats=display_stats
                )
                _, _, _, all_rewards, all_availabilities, durations = epsilon_greedy_search(
                    cyberbattle_env=cyber_env_battle,
                    env_bounds=env_bounds[i],
                    learner=learner,
                    episode_count=10,
                    iteration_count=iteration_count,
                    epsilon=0.0,
                    epsilon_minimum=0.0,
                    title=_agent_name,
                    display_stats=True
                )

                plot_episodes_rewards_averaged(
                    episode_durations=durations,
                    total_rewards=all_rewards,
                    title=_agent_name,
                    ax=axs[0]
                )

                plot_episodes_availability_averaged(
                    episode_durations=durations,
                    total_availabilities=all_availabilities,
                    title=_agent_name,
                    ax=axs[1]
                )

                plot_episodes_length(
                    durations=train_durations,
                    title=_agent_name,
                    ax=axs[2]
                )

            if random_agent:

                all_rewards, all_availabilities, durations = run_random_agent(
                    10, iteration_count, cyber_env_battle)

                plot_episodes_rewards_averaged(
                    episode_durations=durations,
                    total_rewards=all_rewards,
                    title="RandomAgent",
                    ax=axs[0]
                )

                plot_episodes_availability_averaged(
                    episode_durations=durations,
                    total_availabilities=all_availabilities,
                    title="RandomAgent",
                    ax=axs[1]
                )

            _, _, _, all_rewards, all_availabilities, durations = epsilon_greedy_search(
                cyber_env_battle,
                env_bounds,
                CredentialCacheExploiter(),
                "RandomCredentialLookUp",
                episode_count=10,
                iteration_count=iteration_count,
                epsilon=0.0,
                epsilon_minimum=0.0
            )

            plot_episodes_rewards_averaged(
                episode_durations=durations,
                total_rewards=all_rewards,
                title="RandomCredentialLookUp",
                ax=axs[0]
            )

            plot_episodes_availability_averaged(
                episode_durations=durations,
                total_availabilities=all_availabilities,
                title="RandomCredentialLookUp",
                ax=axs[1]
            )

            if plot:

                plt.show()

            if render:

                assert len(render) > 0

                fig.savefig(f'{render}/{environment_names[i][:-3]}')

    elif plot_method == 'envsTOagents':

        _agents = dict()

        for i in range(len(envs)):

            _agents[environment_names[i][:-3]] = {'DQL': DeepQlearner(env_bounds=env_bounds[i],
                                                                      gamma=gamma,
                                                                      replay_memory_size=replay_memory_size,
                                                                      target_update=target_update,
                                                                      batch_size=batch_size,
                                                                      learning_rate=learning_rate),
                                                  'DDQL': DeepQlearner(env_bounds=env_bounds[i],
                                                                       gamma=gamma,
                                                                       replay_memory_size=replay_memory_size,
                                                                       target_update=target_update,
                                                                       batch_size=batch_size,
                                                                       learning_rate=learning_rate,
                                                                       enable_double_dqn=True),
                                                  'QTL': QTabularLearner(env_bounds=env_bounds[i],
                                                                         gamma=gamma,
                                                                         learning_rate=learning_rate),
                                                  'GNN_concat': GNNlearner(env_bounds=env_bounds[i],
                                                                           gamma=gamma,
                                                                           embedding_space_dimension=embedding_space_dimension,
                                                                           replay_memory_size=replay_memory_size,
                                                                           learning_rate=learning_rate,
                                                                           target_update=target_update,
                                                                           batch_size=batch_size,
                                                                           combination_type='concat',
                                                                           num_step=num_step),
                                                  'GNN_GRU': GNNlearner(env_bounds=env_bounds[i],
                                                                        gamma=gamma,
                                                                        embedding_space_dimension=embedding_space_dimension,
                                                                        replay_memory_size=replay_memory_size,
                                                                        learning_rate=learning_rate,
                                                                        target_update=target_update,
                                                                        batch_size=batch_size,
                                                                        combination_type='gru',
                                                                        num_GRU=num_GRU,
                                                                        num_step=num_step),
                                                  "RandomCredentialLookUp": CredentialCacheExploiter()}

            if random_agent:

                _agents['RandomAgent'] = 'RandomAgent'

        for agent_name in _agent_names:

            fig, axs = plt.subplots(3, figsize=(8, 20))
            fig.suptitle(f'Agent : {agent_name}')
            axs[0].set_title(f"Cumulative rewards")
            axs[0].set(xlabel='Iteration', ylabel='Reward')
            axs[1].set_title(f"Network availabilities")
            axs[1].set(xlabel='Iteration', ylabel='Availability')
            axs[2].set_title(f"Length of each episode")
            axs[2].set(xlabel='epoch', ylabel='Iterations number')

            for i, cyber_env_battle in enumerate(envs):

                if agent_name != 'RandomAgent':

                    agent = _agents[environment_names[i][:-3]][agent_name]

                    learner, _, _, _, _, train_durations = epsilon_greedy_search(
                        cyberbattle_env=cyber_env_battle,
                        env_bounds=env_bounds[i],
                        learner=agent,
                        episode_count=training_episode_count,
                        iteration_count=iteration_count,
                        epsilon=epsilon,
                        epsilon_minimum=epsilon_minimum,
                        epsilon_exponential_decay=epsilon_exponential_decay,
                        title=environment_names[i][:-3],
                        display_stats=display_stats
                    )

                    _, _, _, all_rewards, all_availabilities, durations = epsilon_greedy_search(
                        cyberbattle_env=cyber_env_battle,
                        env_bounds=env_bounds[i],
                        learner=learner,
                        episode_count=10,
                        iteration_count=iteration_count,
                        epsilon=0.0,
                        epsilon_minimum=0.0,
                        title=environment_names[i][:-3],
                        display_stats=True
                    )

                    plot_episodes_rewards_averaged(
                        episode_durations=durations,
                        total_rewards=all_rewards,
                        title=environment_names[i][:-3],
                        ax=axs[0]
                    )

                    plot_episodes_availability_averaged(
                        episode_durations=durations,
                        total_availabilities=all_availabilities,
                        title=environment_names[i][:-3],
                        ax=axs[1]
                    )

                    plot_episodes_length(
                        durations=train_durations,
                        title=environment_names[i][:-3],
                        ax=axs[2]
                    )

                    if agent_name == "RandomCredentialLookUp":

                        _, _, _, all_rewards, all_availabilities, durations = epsilon_greedy_search(
                            cyber_env_battle,
                            env_bounds[i],
                            agent,
                            environment_names[i][:-3],
                            episode_count=10,
                            iteration_count=iteration_count,
                            epsilon=0.0,
                            epsilon_minimum=0.0
                        )

                        plot_episodes_rewards_averaged(
                            episode_durations=durations,
                            total_rewards=all_rewards,
                            title=environment_names[i][:-3],
                            ax=axs[0]
                        )

                        plot_episodes_availability_averaged(
                            episode_durations=durations,
                            total_availabilities=all_availabilities,
                            title=environment_names[i][:-3],
                            ax=axs[1]
                        )

                else:

                    all_rewards, all_availabilities, durations = run_random_agent(
                        10, iteration_count, cyber_env_battle)

                    plot_episodes_rewards_averaged(
                        episode_durations=durations,
                        total_rewards=all_rewards,
                        title=environment_names[i][:-3],
                        ax=axs[0]
                    )

                    plot_episodes_availability_averaged(
                        episode_durations=durations,
                        total_availabilities=all_availabilities,
                        title=environment_names[i][:-3],
                        ax=axs[1]
                    )

            if plot:

                plt.show()

            if render:

                assert len(render) > 0

                fig.savefig(f'{render}/{agent_name}')
