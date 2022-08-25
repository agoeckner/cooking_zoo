from gym_cooking.cooking_world.world_objects import *
from gym_cooking.cooking_world.cooking_world import CookingWorld

import numpy as np


class NodeTypes(Enum):
    CHECKPOINT = "Checkpoint"
    ACTION = "Action"


class RecipeNode:

    def __init__(self, root_type, id_num, name, parent=None, conditions=None, contains=None, child_nodes=None):
        self.parent = parent
        self.marked = False
        self.id_num = id_num
        self.root_type = root_type
        self.conditions = conditions or []
        self.contains = contains or []
        self.world_objects = []
        self.name = name
        self.child_nodes = child_nodes or []

    def is_leaf(self):
        return not bool(self.contains)


class Recipe:

    def __init__(self, root_node: RecipeNode, num_goals: int):
        self.root_node = root_node
        self.node_list = [root_node] + self.expand_child_nodes(root_node)
        self.goal_encoding = self.goals_completed(num_goals)
        self.group_marked = []

    def goals_completed(self, num_goals):
        goals = np.zeros(num_goals, dtype=np.int32)
        for node in self.node_list:
            goals[node.id_num] = int(not node.marked)
        return goals

    def get_objects_to_seek(self):
        return []

    def completed(self):
        return self.root_node.marked

    def update_recipe_state(self, world: CookingWorld):
        self.group_marked = []
        for node_tuple in reversed(self.node_list):
            if isinstance(node_tuple, tuple):
                node_markings = []
                for node in node_tuple:
                    previous_marking = node.marking
                    self.update_node(node, world)
                    current_marking = node.marking
                    node_markings.append((previous_marking, current_marking))
                for markings in node_markings:
                    if markings[1]:
                        for node in node_tuple:
                            node.marked = True
                            self.mark_children(node, True)
                        if not markings[0]:
                            self.group_marked.append([len(node_tuple)])
            else:
                self.update_node(node_tuple, world)

    def mark_children(self, node, mark):
        for node_tuple in node.child_nodes:
            if isinstance(node_tuple, tuple):
                for n in node_tuple:
                    n.marked = mark
                    self.mark_children(n, mark)
            else:
                node_tuple.marked = mark
                self.mark_children(node_tuple, mark)

    def update_node(self, node, world):
        node.marked = False
        node.world_objects = []
        if not all((contains.marked for contains in node.contains)):
            return
        for obj in world.world_objects[node.name]:
            # check for all conditions
            if self.check_conditions(node, obj):
                node.world_objects.append(obj)
                node.marked = True

    def expand_child_nodes(self, node: RecipeNode):
        child_nodes = []
        direct_nodes = []
        for child in node.child_nodes:
            if isinstance(child, tuple):
                for n in child:
                    child_nodes.extend(self.expand_child_nodes(n))
                    direct_nodes.append(n)
            else:
                child_nodes.extend(self.expand_child_nodes(child))
                direct_nodes.append(child)
        return direct_nodes + child_nodes

    @staticmethod
    def check_conditions(node: RecipeNode, world_object):
        for condition in node.conditions:
            if getattr(world_object, condition[0]) != condition[1]:
                return False
        else:
            all_contained = []
            for contains in node.contains:
                all_contained.append(any([obj.location == world_object.location for obj in contains.world_objects]))
            return all(all_contained)
