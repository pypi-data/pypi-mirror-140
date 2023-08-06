"""Provide a function to register all pre-built environments."""

import gym

from gym.envs.registration import registry, EnvSpec
from ..env.samples.CyberBattleChain import Chain_env, Chain_IDENTIFIERS
from ..env.samples.CyberBattleToyctf import Toyctf_env, Toyctf_IDENTIFIERS
from ..env.samples.CyberBattleTiny import Tiny_env, Tiny_IDENTIFIERS
from ..env.samples.CyberBattleTinyDeception import Tiny_deception_IDENTIFIERS, Tiny_env_hp_website, Tiny_env_hp_websiteDirectory, Tiny_env_decoy_website, Tiny_env_decoy_websiteDirectory, Tiny_deception_env

from ..env.env_generation.actions import Attacker, Defender
from objects_and_global_functions import *

from ..env.env_generation.Iterative_defender import ScanAndReimageCompromiseMachines


def register(id, entry_point, identifiers, **kwargs):
    """Register an environment in the gym API."""
    if id in registry.env_specs:
        ValueError('Cannot re-register id: {}'.format(id))

    spec = EnvSpec(id, **kwargs)
    spec.ports = identifiers.ports
    spec.properties = identifiers.properties
    spec.local_vulnerabilities = identifiers.local_vulnerabilities
    spec.remote_vulnerabilities = identifiers.remote_vulnerabilities
    spec.entry_point = entry_point

    registry.env_specs[id] = spec


def register_env():
    """Register all used environment during simulations."""
    if 'Chain_env_size4-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size4-v0']

    register('Chain_env_size4-v0',
             identifiers=Chain_IDENTIFIERS,
             entry_point=Chain_env,
             kwargs={'size': 4,
                     'defender_agent': None,
                     'attacker': Attacker(capture_flag=1),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0}
             )

    if 'Chain_env_size4_with_defender-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size4_with_defender-v0']

    register(
        'Chain_env_size4_with_defender-v0',
        identifiers=Chain_IDENTIFIERS,
        entry_point=Chain_env,
        kwargs={
            'size': 4,
            'defender_agent': ScanAndReimageCompromiseMachines(
                probability=0.4,
                scan_capacity=5,
                scan_frequency=8),
            'attacker': Attacker(
                capture_flag=1),
            'defender': Defender(
                eviction=True,
                maintain_sla=0.8),
            'winning_reward': 5000.0,
            'losing_reward': 0.0})

    if 'Chain_env_size10-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size10-v0']

    register('Chain_env_size10-v0',
             identifiers=Chain_IDENTIFIERS,
             entry_point=Chain_env,
             kwargs={'size': 10,
                     'defender_agent': None,
                     'attacker': Attacker(capture_flag=1),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0}
             )

    if 'Chain_env_size10_with_defender-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size10_with_defender-v0']

    register(
        'Chain_env_size10_with_defender-v0',
        identifiers=Chain_IDENTIFIERS,
        entry_point=Chain_env,
        kwargs={
            'size': 10,
            'defender_agent': ScanAndReimageCompromiseMachines(
                probability=0.4,
                scan_capacity=5,
                scan_frequency=8),
            'attacker': Attacker(
                capture_flag=1),
            'defender': Defender(
                eviction=True,
                maintain_sla=0.8),
            'winning_reward': 5000.0,
            'losing_reward': 0.0})

    if 'Chain_env_size20-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size20-v0']

    register('Chain_env_size20-v0',
             identifiers=Chain_IDENTIFIERS,
             entry_point=Chain_env,
             kwargs={'size': 20,
                     'defender_agent': None,
                     'attacker': Attacker(capture_flag=1),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0}
             )

    if 'Chain_env_size20_with_defender-v0' in registry.env_specs:
        del registry.env_specs['Chain_env_size20_with_defender-v0']

    register(
        'Chain_env_size20_with_defender-v0',
        identifiers=Chain_IDENTIFIERS,
        entry_point=Chain_env,
        kwargs={
            'size': 20,
            'defender_agent': ScanAndReimageCompromiseMachines(
                probability=0.4,
                scan_capacity=5,
                scan_frequency=8),
            'attacker': Attacker(
                capture_flag=1),
            'defender': Defender(
                eviction=True,
                maintain_sla=0.8),
            'winning_reward': 5000.0,
            'losing_reward': 0.0})

    if 'Tiny_env-v0' in registry.env_specs:
        del registry.env_specs['Tiny_env-v0']

    register('Tiny_env-v0',
             identifiers=Tiny_IDENTIFIERS,
             entry_point=Tiny_env,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=1),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0}
             )

    if 'Tiny_env_with_defender-v0' in registry.env_specs:
        del registry.env_specs['Tiny_env_with_defender-v0']

    register(
        'Tiny_env_with_defender-v0',
        identifiers=Tiny_IDENTIFIERS,
        entry_point=Tiny_env,
        kwargs={
            'defender_agent': ScanAndReimageCompromiseMachines(
                probability=0.4,
                scan_capacity=5,
                scan_frequency=8),
            'attacker': Attacker(
                capture_flag=1),
            'defender': Defender(
                eviction=True,
                maintain_sla=0.8),
            'winning_reward': 5000.0,
            'losing_reward': 0.0})

    if 'Toyctf_env-v0' in registry.env_specs:
        del registry.env_specs['Toyctf_env-v0']

    register('Toyctf_env-v0',
             identifiers=Toyctf_IDENTIFIERS,
             entry_point=Toyctf_env,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=4),
                     'defender': Defender(),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0}
             )

    if 'Toyctf_env_with_defender-v0' in registry.env_specs:
        del registry.env_specs['Toyctf_env_with_defender-v0']

    register(
        'Toyctf_env_with_defender-v0',
        identifiers=Toyctf_IDENTIFIERS,
        entry_point=Toyctf_env,
        kwargs={
            'defender_agent': ScanAndReimageCompromiseMachines(
                probability=0.4,
                scan_capacity=5,
                scan_frequency=8),
            'attacker': Attacker(
                capture_flag=4),
            'defender': Defender(
                eviction=True,
                maintain_sla=0.8),
            'winning_reward': 5000.0,
            'losing_reward': 0.0})

# Deception environments

    if 'Tiny_Honeypot_Website-v0' in registry.env_specs:
        del registry.env_specs['Tiny_Honeypot_Website-v0']

    register('Tiny_Honeypot_Website-v0',
             identifiers=Tiny_deception_IDENTIFIERS['Website_honeypot'],
             entry_point=Tiny_env_hp_website,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=4),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0,
                     'positive_rewards': False}
             )

    if 'Tiny_Honeypot_WebsiteDirectory-v0' in registry.env_specs:
        del registry.env_specs['Tiny_Honeypot_WebsiteDirectory-v0']

    register(
        'Tiny_Honeypot_Website.Directory-v0',
        identifiers=Tiny_deception_IDENTIFIERS['Website.Directory_honeypot'],
        entry_point=Tiny_env_hp_websiteDirectory,
        kwargs={
            'defender_agent': None,
            'attacker': Attacker(
                capture_flag=4),
            'defender': Defender(
                eviction=True),
            'winning_reward': 5000.0,
            'losing_reward': 0.0,
            'positive_rewards': False})

    if 'Tiny_Decoy_Website-v0' in registry.env_specs:
        del registry.env_specs['Tiny_Decoy_Website-v0']

    register('Tiny_Decoy_Website-v0',
             identifiers=Tiny_deception_IDENTIFIERS['Website_decoy'],
             entry_point=Tiny_env_decoy_website,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=4),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0,
                     'positive_rewards': False}
             )

    if 'Tiny_Decoy_Website.Directory-v0' in registry.env_specs:
        del registry.env_specs['Tiny_Decoy_Website.Directory-v0']

    register('Tiny_Decoy_Website.Directory-v0',
             identifiers=Tiny_deception_IDENTIFIERS['Website.Directory_decoy'],
             entry_point=Tiny_env_decoy_websiteDirectory,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=4),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0,
                     'positive_rewards': False}
             )

    if 'Tiny_Deception_env-v0' in registry.env_specs:
        del registry.env_specs['Tiny_Deception_env-v0']

    register('Tiny_Deception_env-v0',
             identifiers=Tiny_deception_IDENTIFIERS['Deception_env'],
             entry_point=Tiny_deception_env,
             kwargs={'defender_agent': None,
                     'attacker': Attacker(capture_flag=4),
                     'defender': Defender(eviction=True),
                     'winning_reward': 5000.0,
                     'losing_reward': 0.0,
                     'positive_rewards': False}
             )
