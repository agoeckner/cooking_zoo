from gym_cooking.cooking_world.world_objects import *
from gym_cooking.cooking_world.constants import ChopFoodStates


class SequenceObject:

    def __init__(self, obj, precondition, after_condition):
        self.object = obj
        self.precondition = precondition
        self.after_condition = after_condition


class SequenceList:

    def __init__(self, sequence):
        self.sequence = sequence
        self.state = 0

    def finished(self):
        return len(self.sequence) == self.state


class SequenceSet:

    def __init__(self, sequences):
        self.sequences = sequences

"[[[pick carrot, place carrot, cut carrot, pick carrot, place carrot], [pick banana, place banana, cut banana, pick banana, place banana]]. [pick plate, place plate]]"


carrot_pick_so = SequenceObject(Carrot, 
                                [(Agent, "holding", None), (Carrot, "chop_state", ChopFoodStates.FRESH)], 
                                [(Agent, "holding", (Carrot, "chop_state", ChopFoodStates.FRESH))])
place_carrot_so = SequenceObject(Cutboard, 
                                 [(Agent, "holding", Carrot)], 
                                 [(Agent, "holding", None), (Cutboard, "content", [(Carrot, "chop_state", ChopFoodStates.FRESH)])])
cut_carrot_so = SequenceObject(Cutboard, 
                               [(Carrot, "chop_state", ChopFoodStates.FRESH), (Cutboard, "content", [(Carrot, "chop_state", ChopFoodStates.FRESH)])], 
                               [(Carrot, "chop_state", ChopFoodStates.CHOPPED), (Cutboard, "content", [(Carrot, "chop_state", ChopFoodStates.CHOPPED)])])
carrot_chopped_pick_so = SequenceObject(Carrot, 
                                        [(Agent, "holding", None), (Carrot, "chop_state", ChopFoodStates.CHOPPED)], 
                                        [(Agent, "holding", (Carrot, "chop_state", ChopFoodStates.CHOPPED))])
place_chopped_carrot_so = SequenceObject(Plate, 
                                         [(Agent, "holding", (Carrot, "chop_state", ChopFoodStates.CHOPPED))], 
                                         [(Agent, "holding", None), (Plate, "content", [(Carrot, "chop_state", ChopFoodStates.CHOPPED)])])

banana_pick_so = SequenceObject(Banana, 
                                [(Agent, "holding", None), (Banana, "chop_state", ChopFoodStates.FRESH)], 
                                [(Agent, "holding", (Banana, "chop_state", ChopFoodStates.FRESH))])
place_banana_so = SequenceObject(Cutboard, 
                                 [(Agent, "holding", Banana)], 
                                 [(Agent, "holding", None), (Cutboard, "content", [(Banana, "chop_state", ChopFoodStates.FRESH)])])
cut_banana_so = SequenceObject(Cutboard, 
                               [(Banana, "chop_state", ChopFoodStates.FRESH), (Cutboard, "content", [(Banana, "chop_state", ChopFoodStates.FRESH)])], 
                               [(Banana, "chop_state", ChopFoodStates.CHOPPED), (Cutboard, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED)])])
banana_chopped_pick_so = SequenceObject(Banana, 
                                        [(Agent, "holding", None), (Banana, "chop_state", ChopFoodStates.CHOPPED)], 
                                        [(Agent, "holding", (Banana, "chop_state", ChopFoodStates.CHOPPED))])
place_chopped_banana_so = SequenceObject(Plate, 
                                         [(Agent, "holding", (Banana, "chop_state", ChopFoodStates.CHOPPED))], 
                                         [(Agent, "holding", None), (Plate, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED)])])

pick_plate_so = SequenceObject(Plate, [(Agent, "holding", None), (Plate, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED), (Carrot, "chop_state", ChopFoodStates.CHOPPED)])],
                                      [(Agent, "holding", (Plate, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED), (Carrot, "chop_state", ChopFoodStates.CHOPPED)]))])
place_plate_so = SequenceObject(Deliversquare, [(Agent, "holding", (Plate, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED), (Carrot, "chop_state", ChopFoodStates.CHOPPED)]))],
                                               [(Agent, "holding", None), (Deliversquare, "content", (Plate, "content", [(Banana, "chop_state", ChopFoodStates.CHOPPED), (Carrot, "chop_state", ChopFoodStates.CHOPPED)]))])

banana_sequence = SequenceList([banana_pick_so, place_banana_so, cut_banana_so, banana_chopped_pick_so, place_chopped_banana_so])
carrot_sequence = SequenceList([carrot_pick_so, place_carrot_so, cut_carrot_so, carrot_chopped_pick_so, place_chopped_carrot_so])

banana_carrot_sequence_set = SequenceSet({banana_sequence, carrot_sequence})

plate_sequence = SequenceList([pick_plate_so, place_plate_so])
banana_carrot_recipe = SequenceList([banana_carrot_sequence_set, plate_sequence])





