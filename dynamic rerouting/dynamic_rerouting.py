import time
import json
import numpy as np
from VecnaWarehouseEnv import VecnaWarehouseEnv

env = VecnaWarehouseEnv()

EPISODES = 100
MAX_SEQUENCE_LENGTH = 20

env.reset()
env.render()

policy = None

with open("policy.json") as p:
	policy = json.load(p)

# print(policy)

# initial_states = [[4, 6, 12], [4, 6, 5]]

for episode_count in range(EPISODES):
	# observation = env.reset_seq(initial_states, episode_count)
	# print("Episode, ", episode_count, observation)
	observation = env.reset()
	for _ in range(MAX_SEQUENCE_LENGTH):
		# action = env.action_space.sample()
		action = np.argmax(policy[str(observation)])
		observation, reward, done, info = env.step(action)
		time.sleep(1)
		# print(current_state, action, observation, reward)
		if done:
			print("Reached Goal")
			break

env.stop_render()

