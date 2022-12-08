from gym_cooking.environment.cooking_env import parallel_env
from gym_cooking.environment.manual_policy import ManualPolicy
from time import sleep


n_agents = 2
num_humans = 1
max_steps = 100
render = True
obs_spaces = None
action_scheme = "scheme3"
ghost_agents = 0
manual_control = True

level = 'open_room_salad2'
seed = 1
record = False
max_num_timesteps = 1000
recipes = ["TomatoSalad", 'TomatoSalad']

env = parallel_env(level=level, num_agents=n_agents, record=record, max_steps=max_num_timesteps, recipes=recipes,
                   obs_spaces=obs_spaces, action_scheme=action_scheme, ghost_agents=ghost_agents, render=render)

obs = env.reset()

env.render()

action_space = env.action_spaces["player_0"]

manual_policy = ManualPolicy(env, agent_id="player_1")

terminations = {"player_0": False}

cum_sum = 0

idx = 0

while not all(terminations.values()):
    action = {"player_0": 1 if idx % 2 else 2, "player_1": manual_policy("player_1")}
    observations, rewards, terminations, truncations, infos = env.step(action)
    env.render()
    env.unwrapped.screenshot()
    print(rewards)
    print(terminations)
    cum_sum += rewards["player_0"]
    sleep(0.1)
    idx += 1

print(cum_sum)
print("done")
