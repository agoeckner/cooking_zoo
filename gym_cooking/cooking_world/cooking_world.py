from collections import defaultdict
from typing import List
from gym_cooking.cooking_world.world_objects import *

from pathlib import Path
import os.path
import json


class CookingWorld:

    COLORS = ['blue', 'magenta', 'yellow', 'green']

    SymbolToClass = {
        ' ': Floor,
        '-': Counter,
        '/': CutBoard,
        '*': DeliverSquare,
        't': Tomato,
        'l': Lettuce,
        'o': Onion,
        'p': Plate,
        'b': Blender
    }

    def __init__(self, agents, width, height):
        self.agents = agents
        self.width = width
        self.height = height
        self.world_objects = defaultdict(list)
        self.abstract_index = defaultdict(list)

    def add_object(self, obj):
        self.world_objects[type(obj).__name__].append(obj)

    def index_objects(self):
        for type_name, obj_list in self.world_objects.items():
            for abstract_class in ABSTRACT_GAME_CLASSES:
                if issubclass(StringToClass[type_name], abstract_class):
                    self.abstract_index[abstract_class].extend(obj_list)

    def get_object_list(self):
        object_list = []
        for value in self.world_objects.values():
            object_list.extend(value)
        return object_list

    def progress_world(self):
        for obj in self.abstract_index[ProgressingObject]:
            obj.progress()

    def perform_agent_actions(self, agents, actions):
        cleaned_actions = self.check_inbounds(agents, actions)
        collision_actions = self.check_collisions(agents, cleaned_actions)
        for agent, action in zip(agents, collision_actions):
            self.perform_agent_action(agent, action)
        self.progress_world()

    def perform_agent_action(self, agent: Agent, action):
        target_location = (action[0] + agent.location[0], action[1] + agent.location[1])
        if self.square_walkable(target_location):
            agent.move_to(target_location)
        else:
            dynamic_objects = self.get_objects_at(target_location, DynamicObject)
            static_object = self.get_objects_at(target_location, StaticObject)[0]
            if not agent.holding and not dynamic_objects:
                return
            elif agent.holding and not dynamic_objects:
                if static_object.accepts([agent.holding]):
                    agent.put_down(target_location)
            elif not agent.holding and dynamic_objects:
                object_to_grab = self.get_highest_order_object(dynamic_objects)
                if isinstance(static_object, ActionObject):
                    action_done = static_object.action(dynamic_objects)
                    if not action_done:
                        agent.grab(object_to_grab)
                else:
                    agent.grab(object_to_grab)
            elif agent.holding and dynamic_objects:
                self.attempt_merge(agent, dynamic_objects, target_location)

    def get_highest_order_object(self, objects: List[DynamicObject]):
        order = [Container, Food]
        for obj_type in order:
            obj = self.filter_obj(objects, obj_type)
            if obj:
                return obj
        return None

    @staticmethod
    def filter_obj(objects: List[DynamicObject], obj_type):
        filtered_objects = [obj for obj in objects if isinstance(obj, obj_type)]
        if len(filtered_objects) > 1:
            raise Exception(f"Too many {obj_type} in one place!")
        elif len(filtered_objects) == 1:
            return filtered_objects[0]
        else:
            return None

    def check_inbounds(self, agents, actions):
        cleaned_actions = []
        for agent, action in zip(agents, actions):
            new_x = agent.location[0] + action[0]
            new_y = agent.location[1] + action[1]
            if new_x > self.width - 1 or new_x < 0:
                action[0] = 0
            if new_y > self.height - 1 or new_x < 0:
                action[1] = 0
            cleaned_actions.append(action)
        return cleaned_actions

    def check_collisions(self, agents, actions):
        collision_actions = []
        target_locations = []
        walkable = []
        for agent, action in zip(agents, actions):
            target_location = (action[0] + agent.location[0], action[1] + agent.location[1])
            target_walkable = self.square_walkable(target_location)
            end_location = target_location if target_walkable else agent.location
            target_locations.append(end_location)
            walkable.append(target_walkable)
        for idx, (action, target_location, target_walkable) in enumerate(zip(actions, target_locations, walkable)):
            if target_location in target_locations[:idx] + target_locations[idx+1:] and target_walkable:
                collision_actions.append((0, 0))
            else:
                collision_actions.append(action)
        return collision_actions

    def square_walkable(self, location):
        objects = self.get_objects_at(location, StaticObject)
        if len(objects) != 1:
            raise Exception(f"Not exactly one static object at location: {location}")
        return objects[0].walkable

    def get_abstract_object_at(self, location, object_type):
        return [obj for obj in self.abstract_index[object_type] if obj.location == location]

    def get_objects_at(self, location, object_type=None):
        located_objects = []
        for obj_class_string, objects in self.world_objects.items():
            obj_class = StringToClass[obj_class_string]
            if not object_type or not issubclass(obj_class, object_type):
                continue
            for obj in objects:
                if obj.location == location:
                    located_objects.append(obj)
        return located_objects

    def attempt_merge(self, agent: Agent, dynamic_objects: List[DynamicObject], target_location):
        highest_order_obj = self.get_highest_order_object(dynamic_objects)
        if isinstance(highest_order_obj, Container) and isinstance(agent.holding, Food):
            if agent.holding.done():
                highest_order_obj.add_content(agent.holding)
                agent.put_down(target_location)
        if isinstance(highest_order_obj, Food) and isinstance(agent.holding, Container):
            if highest_order_obj.done():
                agent.holding.add_content(highest_order_obj)
                highest_order_obj.move_to(agent.location)

    def load_new_style_level(self, level_name, num_agents):
        my_path = os.path.realpath(__file__)
        dir_name = os.path.dirname(my_path)
        path = Path(dir_name)
        parent = path.parent / f"utils/new_style_level/{level_name}.json"
        with open(parent) as json_file:
            level_object = json.load(json_file)
            json_file.close()
        self.parse_level_layout(level_object)
        self.parse_static_objects(level_object)

    def parse_level_layout(self, level_object):
        level_layout = level_object["LEVEL_LAYOUT"]
        x = 0
        y = 0
        for y, line in enumerate(iter(level_layout.splitlines())):
            for x, char in enumerate(line):
                if char == "-":
                    counter = Counter(location=(x, y))
                    self.add_object(counter)
                else:
                    floor = Floor(location=(x, y))
                    self.add_object(floor)
        self.width = x
        self.height = y

    def parse_static_objects(self, level_object):
        static_objects = level_object["STATIC_OBJECTS"]
        for static_object in static_objects:
            name = list(static_object.keys())[0]
            obj = StringToClass(name)

    def load_level(self, level, num_agents, random=False):
        self.load_new_style_level(level, num_agents)

    def old_load_level(self, level, num_agents, random=False):
        x = 0
        y = 0
        my_path = os.path.realpath(__file__)
        dir_name = os.path.dirname(my_path)
        path = Path(dir_name)
        parent = path.parent / f"utils/levels/{level}.txt"
        agents = []
        # print(parent)
        with parent.open("r") as file:
            # Mark the phases of reading.
            phase = 1
            for line in file:
                line = line.strip('\n')
                if line == '':
                    phase += 1

                # Phase 1: Read in kitchen map.
                elif phase == 1:
                    for x, rep in enumerate(line):
                        # Object, i.e. Tomato, Lettuce, Onion, or Plate.
                        if rep in 'tlop':
                            counter = Counter(location=(x, y))
                            dynamic_object = self.SymbolToClass[rep](location=(x, y))
                            self.add_object(counter)
                            self.add_object(dynamic_object)
                        # GridSquare, i.e. Floor, Counter, Cutboard, Delivery.
                        elif rep in self.SymbolToClass:
                            static_object = self.SymbolToClass[rep](location=(x, y))
                            self.add_object(static_object)
                        else:
                            # Empty. Set a Floor tile.
                            floor = Floor(location=(x, y))
                            self.add_object(floor)
                    y += 1
                # Phase 2: Read in recipe list.
                elif phase == 2:
                    # self.recipes.append(RecipeStore[line]())
                    pass

                # Phase 3: Read in agent locations (up to num_agents).
                elif phase == 3:
                    if len(agents) < num_agents:
                        loc = line.split(' ')
                        agent = Agent((int(loc[0]), int(loc[1])), self.COLORS[len(agents)],
                                      'agent-' + str(len(agents) + 1))
                        agents.append(agent)

        self.agents = agents
        self.width = x + 1
        self.height = y




