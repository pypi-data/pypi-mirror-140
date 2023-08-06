"""Provide a random policy."""

from .utils.agent_wrapper import * 
from ..env.env_generation.cyber_env import * 
import numpy as np 

def exploit_credentialcache(already_tried, observation, log):
    """Return a connect gym action if possible.
    
    Look among discovered credentials if one of them match with a not owned node.
    """
    potential_source_nodes = np.nonzero(observation.nodes_privilegelevel)[0]

    if len(potential_source_nodes) == 0:
        return log, None, already_tried 
    
    source_node = np.random.choice(potential_source_nodes)

    discovered_credentials = np.array(observation.credentials_cache_matrix)
    n_discovered_creds = len(discovered_credentials)

    if n_discovered_creds == 0:
        return log, None, already_tried 

    nodes_not_owned = np.nonzero(observation.nodes_privilegelevel == 0)[0]

    match_port__target_not_owned = [
        c for c in range(n_discovered_creds) if discovered_credentials[c, 0] in nodes_not_owned
        and c not in already_tried
        ]

    if match_port__target_not_owned:
        log += 'found matching cred in the credential cache\n'
        cred = np.random.choice(match_port__target_not_owned)
        target = discovered_credentials[cred, 0]
        port = discovered_credentials[cred, 1]
        already_tried.append(cred)
        
        return log, {'connect': np.array([int(source_node), int(target), int(port), int(cred)])}, already_tried

    else:

        return log, None, already_tried

class CredentialCacheExploiter:
    """Credential Exploiter policy."""

    def __init__(self):
        """Init."""
        self.already_tried = [] 

    def explore(self, wrapped_env):
        """Return a random valid gym action."""
        return "explore", wrapped_env.sample_valid_action([0, 1]), None 
    
    def exploit(self, wrapped_env, observation, log):
        """Exploit the credential cache if possible and return a connect gym action if possible."""
        log, gym_action, self.already_tried = exploit_credentialcache(self.already_tried, observation, log)
        if gym_action:
            if wrapped_env.env.is_action_valid(gym_action, observation.action_mask):
                return log, 'exploit', gym_action, None 
            
            else:
                return log, 'exploit[invalid]->explore', None, None 
        
        else:
            return log, 'exploit[undefined]->explore', None, None

    def parameters_as_string(self):
        """Return nothing."""
        return
    
    def on_step(self, wrapped_env, observation, reward, done, info, action_metadata):
        """Return nothing."""
        return 

    def end_of_episode(self, i_episode, t):
        """Return nothing."""
        return 
