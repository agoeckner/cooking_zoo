from gym_cooking.cooking_book.sequence import SequenceObject, SequenceList, SequenceSet
from gym_cooking.cooking_world.world_objects import *


class RewardCalculator:

    def __init__(self):
        self.scale = 1

    def compute_reward(self, world, agent, sequence: SequenceList):
        so_start = sequence.sequence[sequence.state]
        if isinstance(so_start, SequenceObject):
            pass
        if isinstance(so_start, SequenceList):
            pass
        if isinstance(so_start, SequenceSet):
            pass

        return

    def handle_sequence_object(self, world, agent, sequence_object):
        after_conditions = self.check_conditions(sequence_object.after_condition)

    def handle_sequence_list(self):
        pass

    def handle_sequence_set(self):
        pass

    def check_conditions(self, world, assigned_object_set, conditions):
        fulfilled_list = []
        for condition in conditions:
            first = condition[0]
            first_obj_list = [obj for obj in assigned_object_set if isinstance(obj, first)]
            if not first_obj_list:
                first_obj_list = world.world_objects[ClassToString[first]]
            sub_fulfilled_list = []
            for obj in first_obj_list:
                obj_fulfilled_list = []
                attr = getattr(obj, condition[1])
                if isinstance(attr, list):
                    attr_check_list = []
                    for elem in condition[2]:
                        if isinstance(elem, Tuple):
                            if self.check_conditions(world, assigned_object_set + obj, [elem[2]]):
                                all_list.append(True)
                            else:
                                all_list.append(False)
                                break
                        else:
                            fulfilled =
                else:
                    if isinstance(condition[2], Tuple):
                        if self.check_conditions(world, assigned_object_set + obj, [condition[2]]):
                            pass
                    else:
                        fulfilled = attr == condition[2]
        return all(fulfilled_list)

    def get_objects_with_cond(self, world, cls, ):
