from gym_cooking.cooking_world.world_objects import *
from gym_cooking.cooking_book.recipe2 import Recipe, RecipeNode
from copy import deepcopy


def id_num_generator():
    num = 0
    while True:
        yield num
        num += 1


id_generator = id_num_generator()

#  Basic food Items
# root_type, id_num, parent=None, conditions=None, contains=None
ChoppedLettuce = RecipeNode(root_type=Lettuce, id_num=next(id_generator), name="Lettuce",
                            conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedOnion = RecipeNode(root_type=Onion, id_num=next(id_generator), name="Onion",
                          conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedTomato = RecipeNode(root_type=Tomato, id_num=next(id_generator), name="Tomato",
                           conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedApple = RecipeNode(root_type=Apple, id_num=next(id_generator), name="Apple",
                          conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedCucumber = RecipeNode(root_type=Cucumber, id_num=next(id_generator), name="Cucumber",
                             conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedWatermelon = RecipeNode(root_type=Watermelon, id_num=next(id_generator), name="Watermelon",
                               conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedBanana = RecipeNode(root_type=Banana, id_num=next(id_generator), name="Banana",
                           conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
ChoppedCarrot = RecipeNode(root_type=Carrot, id_num=next(id_generator), name="Carrot",
                           conditions=[("chop_state", ChopFoodStates.CHOPPED)], child_nodes=[])
# MashedCarrot = RecipeNode(root_type=Carrot, id_num=next(id_generator), name="Carrot",
#                           conditions=[("blend_state", BlenderFoodStates.MASHED)])

# Salad Plates
TomatoPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                         contains=[ChoppedTomato], child_nodes=[ChoppedTomato])
LettucePlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                          contains=[ChoppedLettuce], child_nodes=[ChoppedLettuce])

BananaPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                         contains=[ChoppedBanana], child_nodes=[ChoppedBanana])
CarrotPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                         contains=[ChoppedCarrot], child_nodes=[ChoppedCarrot])

ApplePlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                        contains=[ChoppedApple], child_nodes=[ChoppedApple])
WatermelonPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                             contains=[ChoppedWatermelon], child_nodes=[ChoppedWatermelon])

CucumberPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                           contains=[ChoppedCucumber], child_nodes=[ChoppedCucumber])
OnionPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                        contains=[ChoppedOnion], child_nodes=[ChoppedOnion])

TomatoLettucePlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                                contains=[ChoppedTomato, ChoppedLettuce],
                                child_nodes=[ChoppedTomato, ChoppedLettuce, (LettucePlate, TomatoPlate)])

TomatoLettuceOnionPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                                     contains=[ChoppedTomato, ChoppedLettuce, ChoppedOnion],
                                     child_nodes=[ChoppedTomato, ChoppedLettuce, ChoppedOnion,
                                                  (TomatoLettucePlate, TomatoPlate)])

CarrotBananaPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                               contains=[ChoppedCarrot, ChoppedBanana],
                               child_nodes=[ChoppedCarrot, ChoppedBanana, (CarrotPlate, BananaPlate)])

CucumberOnionPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                                contains=[ChoppedCucumber, ChoppedOnion],
                                child_nodes=[ChoppedCucumber, ChoppedOnion, (CucumberPlate, OnionPlate)])

AppleWatermelonPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
                                  contains=[ChoppedApple, ChoppedWatermelon],
                                  child_nodes=[ChoppedApple, ChoppedWatermelon, (ApplePlate, WatermelonPlate)])
# CarrotPlate = RecipeNode(root_type=Plate, id_num=next(id_generator), name="Plate", conditions=None,
#                          contains=[MashedCarrot])

# Delivered Salads
TomatoSalad = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare", conditions=None,
                         contains=[TomatoPlate], child_nodes=[TomatoPlate])
TomatoLettuceSalad = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare",
                                conditions=None, contains=[TomatoLettucePlate], child_nodes=[TomatoLettucePlate])
TomatoLettuceOnionSalad = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare",
                                     conditions=None, contains=[TomatoLettuceOnionPlate], child_nodes=[])

CarrotBanana = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare", conditions=None,
                          contains=[CarrotBananaPlate], child_nodes=[CarrotBananaPlate])
CucumberOnion = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare", conditions=None,
                           contains=[CucumberOnionPlate], child_nodes=[CucumberOnionPlate])
AppleWatermelon = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare", conditions=None,
                             contains=[AppleWatermelonPlate], child_nodes=[AppleWatermelonPlate])
# MashedCarrot = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name="Deliversquare",
#                           conditions=None, contains=[CarrotPlate])

floor = RecipeNode(root_type=Floor, id_num=next(id_generator), name="Floor", conditions=None, contains=[])
no_recipe_node = RecipeNode(root_type=Deliversquare, id_num=next(id_generator), name='Deliversquare', conditions=None,
                            contains=[floor], child_nodes=[])

# this one increments one further and is thus the amount of ids we have given since
# we started counting at zero.
NUM_GOALS = next(id_generator)

RECIPES = {"TomatoSalad": lambda: deepcopy(Recipe(TomatoSalad, NUM_GOALS)),
           "TomatoLettuceSalad": lambda: deepcopy(Recipe(TomatoLettuceSalad, NUM_GOALS)),
           "CarrotBanana": lambda: deepcopy(Recipe(CarrotBanana, NUM_GOALS)),
           "CucumberOnion": lambda: deepcopy(Recipe(CucumberOnion, NUM_GOALS)),
           "AppleWatermelon": lambda: deepcopy(Recipe(AppleWatermelon, NUM_GOALS)),
           "TomatoLettuceOnionSalad": lambda: deepcopy(Recipe(TomatoLettuceOnionSalad, NUM_GOALS)),
           # "MashedCarrot": lambda: deepcopy(Recipe(MashedCarrot)),
           "no_recipe": lambda: deepcopy(Recipe(no_recipe_node, NUM_GOALS))
           }
