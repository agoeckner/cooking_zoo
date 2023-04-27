from gym_cooking.environment import cooking_env

import gym


class GymCookingEnvironment(gym.Env):
    """Environment object for Overcooked."""

    metadata = {'render.modes': ['human'], 'name': "multi_agent_cooking_zoo"}

    def __init__(self, level, meta_file, num_agents, record, max_steps, recipes, step_reward=True, obs_spaces=None, group_finish=False,
                 action_scheme="scheme1", ghost_agents=0, render=False):
        super().__init__()
        self.zoo_env = cooking_env.parallel_env(level, meta_file, num_agents, record, max_steps, recipes, step_reward,
                                                obs_spaces, group_finish=group_finish, action_scheme=action_scheme,
                                                ghost_agents=ghost_agents, render=render)
        self.observation_space = self.zoo_env.observation_spaces["player_0"]
        self.action_space = self.zoo_env.action_spaces["player_0"]

    def step(self, actions):
        action_dict = {f"player_{i}": actions[i] for i in range(len(actions))}
        obs, reward, done, info = self.zoo_env.step(action_dict)
        return [obs[f"player_{i}"] for i in range(len(obs))], [reward[f"player_{i}"] for i in range(len(reward))], \
               [done[f"player_{i}"] for i in range(len(done))], [info[f"player_{i}"] for i in range(len(info))]

    def reset(self):
        obs = self.zoo_env.reset()
        return [obs[f"player_{i}"] for i in range(len(obs))]

    def render(self, mode='human'):
        self.zoo_env.render()

