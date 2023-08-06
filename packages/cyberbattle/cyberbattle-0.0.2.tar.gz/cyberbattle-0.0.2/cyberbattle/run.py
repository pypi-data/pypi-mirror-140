import gym 

from agents.Qlearner import QTabularLearner
from agents.DeepQlearner import DeepQlearner
from agents.GNNlearner import GNNlearner
from agents.utils.agent_policy import epsilon_greedy_search

from utils.env_processing import register_env
from utils.eval_functions import train_and_eval_agents, run_random_agent
from utils.Interface import Player
from utils.objects_and_global_functions import EnvironmentBounds

cyber_env_battle = gym.make('Toyctf_env-v0')

ep = EnvironmentBounds.of_identifiers(
    maximum_node_count=22,
    maximum_total_credentials=22,
    identifiers=cyber_env_battle._CyberBattleEnv__initial_environment.identifiers
)

iteration_count = 5000
training_episode_count = 10
eval_episode_count = 5
gamma = 0.15

DeepQlearner_agent = QTabularLearner(ep, gamma, learning_rate=0.01) #replay_memory_size=1000, batch_size=32, target_update=5,
                        #embedding_space_dimension=10, combination_type='concat')
run_random_agent(1, 50000, cyber_env_battle, plot=True)
epsilon_greedy_search(cyber_env_battle, 
                ep, 
                DeepQlearner_agent, 
                episode_count=training_episode_count, 
                iteration_count=iteration_count, 
                epsilon=.9, 
                epsilon_minimum=0.01, 
                epsilon_exponential_decay=5000,
                title='DeepQlearner',
                display=False,
                plot_results=False,
                display_stats=True)

#env_names = [
#    "Toyctf_Honeypot_Website-v0",
#    "Toyctf_Honeypot_Website.Directory-v0",
#    "Toyctf_Decoy_Website-v0",
#    "Toyctf_Decoy_Website.Directory-v0",
#    "Toyctf_Deception_env-v0"
#]

#train_and_eval_agents(
#    environment_names=env_names,
#    training_episode_count=1,
#    iteration_count=10,
#    batch_size=512,
#    plot_method='envsTOagents',
#    render='C:/Users/EmilienGRILLOT/Desktop/Custom CyberBattle/CyberBattleAgents/render'
#)