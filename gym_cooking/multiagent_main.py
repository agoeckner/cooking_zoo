from gym_cooking.environment.cooking_env import parallel_env
import numpy as np
from time import sleep


n_agents = 2
num_humans = 1
max_steps = 100
render = True
obs_spaces = None
action_scheme = "scheme1"
ghost_agents = 0
manual_control = False

level = 'open_room_salad2'
seed = 1
record = False
max_num_timesteps = 1000
recipes = ["TomatoSalad", 'TomatoSalad']

env = parallel_env(level=level, num_agents=n_agents, record=record, max_steps=max_num_timesteps, recipes=recipes,
                   obs_spaces=obs_spaces, action_scheme=action_scheme, ghost_agents=ghost_agents, render=render)

obs = env.reset()

action_space = env.action_spaces["player_0"]

done = {"player_0": False}

cum_sum = 0

idx = 0

while not all(done.values()):
    action = {"player_0": 1 if idx % 2 else 2, "player_1": 0}
    observations, rewards, terminations, truncations, infos = env.step(action)
    env.render()
    env.unwrapped.screenshot()
    print(rewards)
    cum_sum += rewards["player_0"]
    sleep(0.1)
    idx += 1

print(cum_sum)
print("done")

