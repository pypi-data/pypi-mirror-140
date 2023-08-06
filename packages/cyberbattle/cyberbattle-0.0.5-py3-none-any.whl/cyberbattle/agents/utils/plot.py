"""Provide a kit to display results."""

import matplotlib.pyplot as plt
import numpy as np
from functools import reduce


def new_plot_reward():
    """Prepare a new plot of cumulative rewards."""
    plt.figure(figsize=(10, 8))
    plt.ylabel('cumulative reward', fontsize=20)
    plt.xlabel('step', fontsize=20)
    plt.xticks(size=20)
    plt.yticks(size=20)
    plt.title('Reward vs Time', fontsize=12)


def new_plot_availability():
    """Prepare a new plot of cumulative rewards."""
    plt.figure(figsize=(10, 8))
    plt.ylabel('network availability', fontsize=20)
    plt.xlabel('step', fontsize=20)
    plt.xticks(size=20)
    plt.yticks(size=20)
    plt.title('Availability vs Time', fontsize=12)


def pad(array, length):
    """Pad an array with 0s to make it of desired length."""
    padding = np.zeros((length,))
    padding[:len(array)] = array
    return padding


def plot_episodes_rewards_averaged(
        episode_durations,
        total_rewards,
        title,
        ax=None):
    """Plot cumulative rewards for a given set of specified episodes."""
    max_iteration_count = np.max(episode_durations) + 1

    all_episodes_rewards_padded = [
        pad(rewards, max_iteration_count) for rewards in total_rewards]
    cumrewards = np.cumsum(all_episodes_rewards_padded, axis=1)
    avg = np.average(cumrewards, axis=0)
    std = np.std(cumrewards, axis=0)
    x = [i for i in range(len(std))]

    if ax:

        ax.plot(x, avg, label=title)
        ax.fill_between(x, avg - std, avg + std, alpha=0.5)
        ax.legend(loc='lower right')

    else:

        plt.plot(x, avg, label=title)
        plt.fill_between(x, avg - std, avg + std, alpha=0.5)
        plt.legend(loc="lower right")
        plt.show()


def fill_with_latest_value(array, length):
    """Fill an array by the right with the edge value."""
    pad = length - len(array)
    if pad > 0:
        return np.pad(array, (0, pad), mode='edge')
    else:
        return array


def plot_episodes_availability_averaged(
        episode_durations,
        total_availabilities,
        title,
        ax=None):
    """Plot availability for a given set of specified episodes."""
    longest_episode_length = np.max(episode_durations) + 1

    all_episodes_padded = [fill_with_latest_value(
        av, longest_episode_length) for av in total_availabilities]
    avg = np.average(all_episodes_padded, axis=0)
    std = np.std(all_episodes_padded, axis=0)
    x = [i for i in range(len(std))]

    if ax:

        ax.plot(x, avg, label=title)
        ax.fill_between(x, avg - std, avg + std, alpha=0.5)
        ax.legend(loc='lower right')

    else:

        plt.plot(x, avg, label=title)
        plt.fill_between(x, avg - std, avg + std, alpha=0.5)
        plt.legend(loc="lower right")
        plt.show()


def plot_episodes_length(durations, title, ax=None):
    """Plot length of every episode."""
    nb_epoch = len(durations)

    if ax:

        ax.plot(range(nb_epoch), durations, label=title)
        ax.legend(loc='lower right')

    else:

        plt.plot(range(nb_epoch), durations, label=title)
        plt.legend(loc="upper right")
        plt.show()


def plot_each_episode(results):
    """Plot cumulative rewards for each episode."""
    for i, episode in enumerate(results['all_episodes_rewards']):
        cumrewards = np.cumsum(episode)
        x = [i for i in range(len(cumrewards))]
        plt.plot(x, cumrewards, label=f'Episode {i}')


def new_plot_loss():
    """Plot MSE loss averaged over all episodes."""
    plt.figure(figsize=(10, 8))
    plt.ylabel('loss', fontsize=20)
    plt.xlabel('episodes', fontsize=20)
    plt.xticks(size=12)
    plt.yticks(size=20)
    plt.title("Loss", fontsize=12)


def plot_all_episodes_loss(all_episodes_losses, name, label):
    """Plot loss for one learning episode."""
    x = [i for i in range(len(all_episodes_losses))]
    plt.plot(x, all_episodes_losses, label=f'{name} {label}')


def running_mean(x, size):
    """Return moving average of x for a window of lenght 'size'."""
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[size:] - cumsum[:-size]) / float(size)


class PlotTraining:
    """Plot training-related stats."""

    def __init__(self, title):
        """Init."""
        self.episode_durations = []
        self.title = title
        self.total_rewards = []
        self.total_availabilities = []

    def plot_end(self):
        """Plot rewards and availabilities through different episodes."""
        new_plot_reward()
        plot_episodes_rewards_averaged(
            self.episode_durations,
            self.total_rewards,
            self.title)
        plt.show()
        new_plot_availability()
        plot_episodes_availability_averaged(
            self.episode_durations,
            self.total_availabilities,
            self.title)
        plt.show()

    def episode_done(self, length, rewards, availabilities):
        """Reset all."""
        self.episode_durations.append(length)
        self.total_rewards.append(rewards)
        self.total_availabilities.append(availabilities)


def length_of_all_episodes(run):
    """Get the length of every episode."""
    return [len(e) for e in run['all_episodes_rewards']]


def reduce(x, desired_width):
    """Average the split in the wished dimension."""
    return [np.average(c) for c in np.array_split(x, desired_width)]


def episodes_rewards_averaged(run):
    """Plot cumulative rewards for a given set of specified episodes."""
    max_iteration_count = np.max([len(r) for r in run['all_episodes_rewards']])
    all_episodes_rewards_padded = [
        pad(rewards, max_iteration_count) for rewards in run['all_episodes_rewards']]
    cumrewards = np.cumsum(all_episodes_rewards_padded, axis=1)
    avg = np.average(cumrewards, axis=0)
    return list(avg)


def episodes_lengths_for_all_runs(all_runs):
    """Return length of all runs."""
    return [length_of_all_episodes(run) for run in all_runs]


def averaged_cummulative_rewards(all_runs, width):
    """Return averaged cummulative rewards of all runs."""
    return [reduce(episodes_rewards_averaged(run), width) for run in all_runs]
