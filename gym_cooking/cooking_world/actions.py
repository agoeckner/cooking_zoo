
class ActionScheme1:

    WALK_UP = 4
    WALK_DOWN = 3
    WALK_RIGHT = 2
    WALK_LEFT = 1

    NO_OP = 0

    INTERACT_PRIMARY = 5
    INTERACT_PICK_UP_SPECIAL = 6
    EXECUTE_ACTION = 7

    WALK_ACTIONS = [WALK_UP, WALK_DOWN, WALK_RIGHT, WALK_LEFT]
    INTERACT_ACTIONS = [INTERACT_PRIMARY, INTERACT_PICK_UP_SPECIAL, EXECUTE_ACTION]
    ACTIONS = [NO_OP, WALK_LEFT, WALK_RIGHT, WALK_DOWN, WALK_UP, INTERACT_PRIMARY, INTERACT_PICK_UP_SPECIAL, EXECUTE_ACTION]


class ActionScheme2:

    WALK = 3
    TURN_RIGHT = 2
    TURN_LEFT = 1

    NO_OP = 0
    NO_OP2 = 4

    INTERACT_PRIMARY = 5
    INTERACT_PICK_UP_SPECIAL = 6
    EXECUTE_ACTION = 7

    WALK_ACTIONS = [WALK, TURN_RIGHT, TURN_LEFT]
    INTERACT_ACTIONS = [INTERACT_PRIMARY, INTERACT_PICK_UP_SPECIAL, EXECUTE_ACTION]
    ACTIONS = [NO_OP, NO_OP2, TURN_LEFT, TURN_RIGHT, WALK, INTERACT_PRIMARY, INTERACT_PICK_UP_SPECIAL,
               EXECUTE_ACTION]
