from gym_cooking.environment.cooking_env import parallel_env
from gym_cooking.environment.manual_policy import ManualPolicy
from time import sleep


n_agents = 2
num_humans = 1
max_steps = 400
render = True
obs_spaces = ["feature_vector"]
action_scheme = "scheme3"
ghost_agents = 0
manual_control = False
record = False
meta_file = "experiment"
level = "separated_room_experiment"
recipes = ["TomatoLettuceSalad", "CarrotBanana"]

env = parallel_env(level=level, meta_file=meta_file, num_agents=n_agents, record=record, max_steps=max_steps, recipes=recipes,
                   obs_spaces=obs_spaces, action_scheme=action_scheme, ghost_agents=ghost_agents, render=render)

obs = env.reset()

env.render()

action_space = env.action_spaces["player_0"]

manual_policy = ManualPolicy(env, agent_id="player_1")

terminations = {"player_0": False}

cum_sum = 0

idx = 0

while not all(terminations.values()):
    action = {"player_1": action_space.sample(), "player_0": manual_policy("player_1")}
    observations, rewards, terminations, truncations, infos = env.step(action)
    env.render()
    env.unwrapped.screenshot()
    print(rewards)
    print(terminations)
    print(truncations)
    cum_sum += rewards["player_0"]
    sleep(0.1)
    idx += 1

print(cum_sum)
print("done")
