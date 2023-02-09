from gym_cooking.environment.manual_policy import ManualPolicy
from gym_cooking.environment import cooking_env

n_agents = 1
num_humans = 1
max_steps = 400
render = True
obs_spaces = ["feature_vector"]
action_scheme = "scheme3"
ghost_agents = 0
manual_control = False
record = False
meta_file = "example"
level = "separated_room_experiment"
recipes = ["MashedCarrotBanana"]  # "CarrotBanana"

env = cooking_env.parallel_env(level=level, meta_file=meta_file, num_agents=n_agents, record=record,
                               max_steps=max_steps, recipes=recipes, obs_spaces=obs_spaces,
                               action_scheme=action_scheme, ghost_agents=ghost_agents, render=render)

env.reset()
env.render()

terminations = {"player_0": False}

manual_policy = ManualPolicy(env, agent_id="player_0")

while not all(terminations.values()):
    action = {"player_0": manual_policy("player_0")}
    observations, rewards, terminations, truncations, infos = env.step(action)
    env.render()

