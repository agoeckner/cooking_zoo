from gym_cooking.cooking_world.world_objects import *
from gym_cooking.cooking_world.constants import ChopFoodStates


class State:

    def __init__(self, objects_to_seek, world_state, transition_condition):
        self.objects_to_seek = []
        self.internal_state = []
        self.transition_condition = []


class SequenceObject:

    def __init__(self, obj, precondition, after_condition):
        self.object = obj
        self.precondition = precondition
        self.after_condition = after_condition

"[[[pick carrot, place carrot, cut carrot, pick carrot, place carrot], [pick banana, place banana, cut banana, pick banana, place banana]]. [pick plate, place plate]]"



carrot_pick_so = SequenceObject(Carrot, [("hold", None), (Carrot, ChopFoodStates.FRESH)], [("hold", Carrot), (Carrot, ChopFoodStates.FRESH)])
place_carrot_so = SequenceObject(Cutboard, [("hold", Carrot)], [("hold", None)])
cut_carrot_so = SequenceObject(Cutboard, [Carrot, ChopFoodStates.FRESH], [(Carrot, ChopFoodStates.CHOPPED)])
carrot_chopped_pick_so = SequenceObject(Carrot, [("hold", None), (Carrot, ChopFoodStates.CHOPPED)], [("hold", Carrot), (Carrot, ChopFoodStates.CHOPPED)])
place_chopped_carrot_so = SequenceObject(Plate, [("hold", Carrot)], [("hold", None)])
cutboard_carrot_so = SequenceObject(Cutboard, [("self", "hold", Carrot)], [])



state1 = State([Carrot], [], [(Carrot, ChopFoodStates.CHOPPED), (Banana, ChopFoodStates.CHOPPED)])
state2 = State()
state3 = State()
sequence_banana_carrot = [[("Carrot", ChopFoodStates.FRESH), ("Banana", ChopFoodStates.FRESH)], []]



