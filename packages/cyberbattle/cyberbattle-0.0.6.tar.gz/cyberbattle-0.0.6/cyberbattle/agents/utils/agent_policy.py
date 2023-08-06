"""Helpers for training agents."""

from .agent_wrapper import *
import math

from .plot import PlotTraining

from ..GNNlearner import GNNlearner


def run_random_agent(episode_count, iteration_count, gym_env, plot=False):
    """Run a simple random agent on the specified gym environment and.

    plot exploration graph and reward function
    """
    log = ''
    plot_title = (f"###### RandomAgent\n"
                  f"Learning with: episode_count={episode_count},"
                  f"iteration_count={iteration_count},")

    durations = []
    all_rewards = []
    all_availability = []

    plottraining = PlotTraining(title=plot_title)
    for _ in range(episode_count):
        _ = gym_env.reset()
        total_reward = 0.0
        rewards = []
        availability = []
        episode_ended_at = None

        for t in range(iteration_count):
            action = gym_env.sample_valid_action()

            log, _, reward, done, info = gym_env.step(action, log)

            rewards.append(reward)
            availability.append(info['network availability'])
            total_reward += reward

            if done:
                episode_ended_at = t
                break

        length = episode_ended_at if episode_ended_at else iteration_count
        plottraining.episode_done(length, all_rewards, all_availability)
        durations.append(length)
        all_rewards.append(rewards)
        all_availability.append(availability)

    if plot:
        print(log)
        plottraining.plot_end()
        print("simulation ended")

    gym_env.close()

    return all_rewards, all_availability, durations


def print_stats(stats):
    """Print learning statistics."""
    def print_breakdown(stats, actiontype: str):
        def ratio(kind: str) -> str:
            x, y = stats[actiontype]['reward'][kind], stats[actiontype]['noreward'][kind]
            sum = x + y
            if sum == 0:
                return 'NaN'
            else:
                return f"{(x / sum):.2f}"

        def print_kind(kind: str):
            print(
                f"    {actiontype}-{kind}: {stats[actiontype]['reward'][kind]}/{stats[actiontype]['noreward'][kind]} "
                f"({ratio(kind)})")
        print_kind('local')
        print_kind('remote')
        print_kind('connect')

    print("  Breakdown [Reward/NoReward (Success rate)]")
    print_breakdown(stats, 'explore')
    print_breakdown(stats, 'exploit')
    print(
        f"  exploit deflected to exploration: {stats['exploit_deflected_to_explore']}")


def epsilon_greedy_search(
    cyberbattle_env,
    env_bounds,
    learner,
    title,
    episode_count,
    iteration_count,
    epsilon,
    epsilon_minimum,
    epsilon_multdecay=None,
    epsilon_exponential_decay=None,
    display=False,
    plot_results=False,
    display_stats=False
):
    """Train the agent with an epsilon greedy policy."""
    print(title)

    log = ''

    plot_title = (
        f"###### {title}\n"
        f"Learning with: episode_count={episode_count},"
        f"iteration_count={iteration_count},"
        f"ϵ={epsilon},"
        f'ϵ_min={epsilon_minimum}, '
        f'ϵ_multdecay={epsilon_multdecay}, ' if epsilon_multdecay else ''
        f'ϵ_expdecay={epsilon_exponential_decay},' if epsilon_exponential_decay else ''
        f"{learner.parameters_as_string()}")

    plottraining = PlotTraining(title=plot_title)

    initial_epsilon = epsilon

    if isinstance(learner, GNNlearner):
        state_tracker = ActionTrackingStateAugmentationGNN(
            env_bounds, cyberbattle_env.reset())

    else:
        state_tracker = ActionTrackingStateAugmentation(
            env_bounds, cyberbattle_env.reset())

    wrapped_env = AgentWrapper(
        cyberbattle_env, state_tracker)

    steps_done = 0
    durations = []
    all_rewards = []
    all_availabilities = []

    for i_episode in range(1, episode_count + 1):

        print('Epoch {}/{}, ϵ={}'.format(i_episode, episode_count, epsilon))

        observation = wrapped_env.reset()
        total_reward = 0.0
        # learner.new_episode()

        stats = {'exploit': {'reward': {'local': 0, 'remote': 0, 'connect': 0},
                             'noreward': {'local': 0, 'remote': 0, 'connect': 0}},
                 'explore': {'reward': {'local': 0, 'remote': 0, 'connect': 0},
                             'noreward': {'local': 0, 'remote': 0, 'connect': 0}},
                 'exploit_deflected_to_explore': 0}

        episode_ended_at = None
        rewards = []
        availabilities = []

        for t in range(1, iteration_count + 1):

            if epsilon_exponential_decay:
                epsilon = epsilon_minimum + \
                    math.exp(-1 * steps_done / epsilon_exponential_decay) * \
                    (initial_epsilon - epsilon_minimum)

            steps_done += 1

            x = np.random.rand()
            if x <= epsilon:
                action_style, gym_action, action_metadata = learner.explore(
                    wrapped_env)
            else:
                log_exploit, action_style, gym_action, action_metadata = learner.exploit(
                    wrapped_env, observation, log)

                if not gym_action:
                    stats['exploit_deflected_to_explore'] += 1
                    _, gym_action, action_metadata = learner.explore(
                        wrapped_env)

                else:
                    log = log_exploit

            log, observation, reward, done, info = wrapped_env.step(
                gym_action, log)
            action_type = 'exploit' if action_style == 'exploit' else 'explore'

            outcome = 'reward' if reward > 0 else 'noreward'

            if 'local_vulnerability' in gym_action:
                stats[action_type][outcome]['local'] += 1
            elif 'remote_vulnerability' in gym_action:
                stats[action_type][outcome]['remote'] += 1
            else:
                stats[action_type][outcome]['connect'] += 1

            learner.on_step(
                wrapped_env,
                observation,
                reward,
                done,
                info,
                action_metadata)

            assert np.shape(reward) == ()

            rewards.append(reward)
            availabilities.append(info['network availability'])
            total_reward += reward

            log += 'total_reward : {}\n'.format(total_reward)

            if done:
                episode_ended_at = t
                break

        length = episode_ended_at if episode_ended_at else iteration_count
        print(
            'End of epoch {} : iterations number={}, total rewards={}'.format(
                i_episode,
                length,
                total_reward))
        #loss_string = learner.loss_as_string()
        # if loss_string:
        #    log += "\nloss={}\n".format(loss_string)
        if display_stats:

            print_stats(stats)

        learner.end_of_episode(i_episode, length)
        plottraining.episode_done(length, rewards, availabilities)
        durations.append(length)
        all_rewards.append(rewards)
        all_availabilities.append(availabilities)

        if epsilon_multdecay:
            epsilon = max(epsilon_minimum, epsilon * epsilon_multdecay)

    if display:

        print(log)
        print('Simulation ended')

    if plot_results:
        plottraining.plot_end()

    return learner, cyberbattle_env.name, title, all_rewards, all_availabilities, durations
