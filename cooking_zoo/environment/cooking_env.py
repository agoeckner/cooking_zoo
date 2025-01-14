# Other core modules
import copy

from cooking_zoo.cooking_world.cooking_world import CookingWorld
from cooking_zoo.cooking_world.world_objects import *
from cooking_zoo.cooking_world.actions import *
from cooking_zoo.cooking_book.recipe_drawer import RECIPES, NUM_GOALS, RECIPE_STORE, DEFAULT_NUM_GOALS

import numpy as np
from collections import namedtuple, defaultdict
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn
from gymnasium.utils import seeding
from cooking_zoo.environment.game.graphic_pipeline import GraphicPipeline
import gymnasium as gym


CollisionRepr = namedtuple("CollisionRepr", "time agent_names agent_locations")
COLORS = ['blue', 'magenta', 'yellow', 'green']

FPS = 20


def env(level, meta_file, num_agents, max_steps, recipes, agent_visualization=None, obs_spaces=None,
        end_condition_all_dishes=False, action_scheme="scheme1", render=False, reward_scheme=None):
    """
    The env function wraps the environment in 3 wrappers by default. These
    wrappers contain logic that is common to many pettingzoo environments.
    We recommend you use at least the OrderEnforcingWrapper on your own environment
    to provide sane error messages. You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    env_init = CookingEnvironment(level, meta_file, num_agents, max_steps, recipes, agent_visualization,
                                  obs_spaces, end_condition_all_dishes=end_condition_all_dishes,
                                  action_scheme=action_scheme, render=render, reward_scheme=reward_scheme)
    env_init = wrappers.CaptureStdoutWrapper(env_init)
    env_init = wrappers.OrderEnforcingWrapper(env_init)
    return env_init


parallel_env = parallel_wrapper_fn(env)


class CookingEnvironment(AECEnv):
    """Environment object for Overcooked."""

    metadata = {
        "render_modes": ["human", "rgb_array"],
        'render.modes': ['human', "rgb_array"],
        "name": "cookingzoo_v1",
        "is_parallelizable": True,
        "render_fps": FPS,
    }

    action_scheme_map = {"scheme1": ActionScheme1, "scheme2": ActionScheme2, "scheme3": ActionScheme3}

    def __init__(self, level, meta_file, num_agents, max_steps, recipes, agent_visualization=None, obs_spaces=None,
                 end_condition_all_dishes=False, allowed_objects=None, action_scheme="scheme1", render=False,
                 reward_scheme=None):
        super().__init__()

        obs_spaces = obs_spaces or ["feature_vector"]
        self.allowed_obs_spaces = ["symbolic", "full", "feature_vector"]
        self.action_scheme = action_scheme
        self.action_scheme_class = self.action_scheme_map[self.action_scheme]
        assert len(set(obs_spaces + self.allowed_obs_spaces)) == 3, \
            f"Selected invalid obs spaces. Allowed {self.allowed_obs_spaces}"
        assert len(obs_spaces) != 0, f"Please select an observation space from: {self.allowed_obs_spaces}"
        self.obs_spaces = obs_spaces
        self.allowed_objects = allowed_objects or []
        self.possible_agents = ["player_" + str(r) for r in range(num_agents)]
        self.agents = self.possible_agents[:]
        self.agent_visualization = agent_visualization or ["human"] * num_agents
        self.reward_scheme = reward_scheme or {"recipe_reward": 20, "max_time_penalty": -5, "recipe_penalty": -40,
                                               "recipe_node_reward": 0}

        self.level = level
        self.max_steps = max_steps
        self.t = 0
        self.filename = ""
        self.set_filename()
        self.meta_file = meta_file
        self.world = CookingWorld(self.action_scheme_class, meta_file)
        assert self.num_agents <= self.world.meta_object_information["Agent"], \
            "Too many agents for this level"
        self.recipes = recipes
        self.graphic_pipeline = None
        self.game = None
        self.render_flag = render
        if RECIPE_STORE:
            self.recipes = RECIPE_STORE
            self.num_goals = NUM_GOALS
        else:
            self.recipes = RECIPES
            self.num_goals = DEFAULT_NUM_GOALS
        self.recipe_graphs = [self.recipes[recipe]() for recipe in recipes]

        self.termination_info = ""
        self.world.load_level(level=self.level, num_agents=num_agents)
        self.graph_representation_length = sum([cls.state_length() for cls in GAME_CLASSES])
        objects = defaultdict(list)
        objects.update(self.world.world_objects)
        objects["Agent"] = self.world.agents
        self.feature_vector_representation_length = 0
        for name, num in self.world.meta_object_information.items():
            cls = StringToClass[name]
            self.feature_vector_representation_length += cls.feature_vector_length() * num
        numeric_obs_space = {'feature_vector': gym.spaces.Box(low=0, high=10,
                                                              shape=(self.world.width, self.world.height,
                                                                     self.graph_representation_length), dtype=np.int32),
                             'agent_location': gym.spaces.Box(low=0, high=max(self.world.width, self.world.height),
                                                              shape=(2,)),
                             'goal_vector': gym.spaces.MultiBinary(self.num_goals)}
        self.feature_obs_space = gym.spaces.Box(low=-1, high=1,
                                                shape=(self.feature_vector_representation_length,))
        obs_space_dict = {"full": numeric_obs_space,
                          "feature_vector": self.feature_obs_space}
        self.observation_spaces = {agent: obs_space_dict[obs_space]
                                   for agent, obs_space in zip(self.possible_agents, self.obs_spaces)}
        self.action_spaces = {agent: gym.spaces.Discrete(len(self.action_scheme_class.ACTIONS))
                              for agent in self.possible_agents}
        self.has_reset = True
        self.end_condition_all_dishes = end_condition_all_dishes

        self.recipe_mapping = dict(zip(self.possible_agents, self.recipe_graphs))
        self.agent_name_mapping = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))
        self.world_agent_mapping = dict(zip(self.possible_agents, self.world.agents))
        self.world_agent_to_env_agent_mapping = dict(zip(self.world.agents, self.possible_agents))
        self.agent_selection = None
        self._agent_selector = agent_selector(self.agents)
        self.done = False
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.accumulated_actions = []
        self.current_tensor_observation = np.zeros((self.world.width, self.world.height,
                                                    self.graph_representation_length))
        self.render_mode = "human"
        self.np_random = None
        self.loaded_recipes = []
        if not RECIPE_STORE:
            self.loaded_recipes = list(RECIPES.keys())
        else:
            self.loaded_recipes = list(RECIPE_STORE.keys())
        # get index of recipe in recipe_list
        idx = [self.loaded_recipes.index(recipe) for recipe in self.recipes]
        # get one hot numpy vector
        self.goal_vectors = dict(zip(self.agents, [np.eye(len(self.loaded_recipes))[i] for i in idx]))

    def set_filename(self):
        self.filename = f"{self.level}_agents{self.num_agents}"

    def state(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    def reset(self, seed=None, return_info=False, options=None):
        options = options or {"full_reset": True}
        # self.world = CookingWorld(self.action_scheme_class)
        self.t = 0

        # For tracking data during an episode.
        self.termination_info = ""

        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        
        # Load world & distances.
        if options["full_reset"]:
            self.world = CookingWorld(self.action_scheme_class, self.meta_file)
        self.world.load_level(level=self.level, num_agents=self.num_agents)

        for recipe in self.recipe_graphs:
            recipe.update_recipe_state(self.world)

        # Get an image observation
        self.recipe_mapping = dict(zip(self.possible_agents, self.recipe_graphs))
        self.agent_name_mapping = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))
        self.world_agent_mapping = dict(zip(self.possible_agents, self.world.agents))
        self.world_agent_to_env_agent_mapping = dict(zip(self.world.agents, self.possible_agents))
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.accumulated_actions = []

    def close(self):
        return

    def step(self, action):
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            self._was_dead_step(action)
            return
        agent = self.agent_selection
        self.accumulated_actions.append(action)
        for idx, agent in enumerate(self.agents):
            self.rewards[agent] = 0
        if self._agent_selector.is_last():
            self.accumulated_step(self.accumulated_actions)
            self.accumulated_actions = []
        self.agent_selection = self._agent_selector.next()
        # self._cumulative_rewards[agent] = 0
        self._cumulative_rewards[agent] += self.rewards[agent]

    def accumulated_step(self, actions):
        # Track internal environment info.
        self.t += 1
        # translated_actions = [action_translation_dict[actions[f"player_{idx}"]] for idx in range(len(actions))]
        self.world.world_step(self.world.agents, actions)

        info = {"t": self.t, "termination_info": self.termination_info}

        dones, rewards, goals, infos = self.compute_rewards()
        for idx, agent in enumerate(self.agents):
            self.terminations[agent] = dones[idx]
            self.rewards[agent] = rewards[idx]
            self.infos[agent] = {"goal_vector": self.goal_vectors[agent], **info, **infos[idx]}

    def observe(self, agent):
        observation = []
        if "full" in self.obs_spaces:
            num_observation = {'feature_vector': self.current_tensor_observation,
                               'agent_location': np.asarray(self.world_agent_mapping[agent].location, np.int32),
                               'goal_vector': self.recipe_mapping[agent].goals_completed(self.num_goals)}
            observation.append(num_observation)
        if "symbolic" in self.obs_spaces:
            objects = defaultdict(list)
            objects.update(self.world.world_objects)
            objects["Agent"] = self.world.agents
            sym_observation = copy.deepcopy(objects)
            observation.append(sym_observation)
        if "feature_vector" in self.obs_spaces:
            observation.append(self.get_feature_vector(agent))
        returned_observation = observation if not len(observation) == 1 else observation[0]
        return returned_observation

    def compute_rewards(self):
        dones = [False] * len(self.recipes)
        rewards = [0] * len(self.recipes)
        open_goals = [[0]] * len(self.recipes)
        # Done if the episode maxes out
        if self.t >= self.max_steps and self.max_steps:
            self.termination_info = f"Terminating because {self.max_steps} timesteps passed"
            # change every entry in dones to true
            dones = [True] * len(self.recipes)



        for idx, recipe in enumerate(self.recipe_graphs):
            goals_before = recipe.goals_completed(self.num_goals)
            completion_before = recipe.completed()
            recipe.update_recipe_state(self.world)
            open_goals[idx] = recipe.goals_completed(self.num_goals)
            malus = not recipe.completed() and completion_before
            bonus = recipe.completed() and not completion_before
            rewards[idx] += (sum(goals_before) - sum(open_goals[idx])) * self.reward_scheme["recipe_node_reward"]
            rewards[idx] += bonus * self.reward_scheme["recipe_reward"]
            rewards[idx] += malus * self.reward_scheme["recipe_penalty"]
            rewards[idx] += (self.reward_scheme["max_time_penalty"] / self.max_steps)

        recipe_evaluations = [recipe.completed() for recipe in self.recipe_graphs]
        infos = [{f"recipe_done": evaluation} for evaluation in recipe_evaluations]
        if self.end_condition_all_dishes:
            recipe_dones = all([recipe.completed() for recipe in self.recipe_graphs])
        else:
            recipe_dones = any([recipe.completed() for recipe in self.recipe_graphs])
        dones = [recipe_dones or done for done in dones]
        return dones, rewards, open_goals, infos

    def get_feature_vector(self, agent):
        feature_vector = []
        objects = defaultdict(list)
        objects.update(self.world.world_objects)
        objects["Agent"] = self.world.agents
        x, y = self.world_agent_mapping[agent].location
        for name, num in self.world.meta_object_information.items():
            cls = StringToClass[name]
            current_num = 0
            for obj in objects[ClassToString[cls]]:
                features = list(obj.feature_vector_representation())
                if features and obj is not self.world_agent_mapping[agent]:
                    features[0] = (features[0] - x) / self.world.width
                    features[1] = (features[1] - y) / self.world.height
                if obj is self.world_agent_mapping[agent]:
                    features[0] = features[0] / self.world.width
                    features[1] = features[1] / self.world.height
                feature_vector.extend(features)
                current_num += 1
            feature_vector.extend([0] * (num - current_num) * cls.feature_vector_length())
        new_vector = np.array(feature_vector)
        return new_vector

    def get_agent_names(self):
        return [agent.name for agent in self.world.agents]

    def render(self, **kwargs):
        if not self.graphic_pipeline:
            self.graphic_pipeline = GraphicPipeline(self.world, self.agent_visualization, self.render_flag)
            self.graphic_pipeline.initialize()
        self.graphic_pipeline.render(self.render_flag)

    def screenshot(self, path="screenshot.png"):
        self.graphic_pipeline.save_image(path)
