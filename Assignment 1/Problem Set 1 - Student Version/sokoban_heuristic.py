from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use

def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.get_actions" HERE.
    # Calling it here will mess up the tracking of the expanded nodes count
    # which is the number of get_actions calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    # NotImplemented()

    # Use the problem.cache() dictionary to store information between calls
    cache = problem.cache()
    
    # Check if the heuristic values are already cached for the current state
    if state in cache:
        return cache[state] # returns the cached value to avoid recomputing.

    if problem.is_goal(state):
        return 0.0 # if state is goal state

    # Calculate the Manhattan distance from each crate to its nearest goal
    heuristic_value = 0
    for crate in state.crates:

        # Check if crate is a goal
        if crate in state.layout.goals:
            continue

        # Check if there is a deadlock
        if is_deadlock(problem, state, crate):
            cache[state] = float('inf')
            return float('inf')
        
        min_distance = float('inf')
        for goal in problem.layout.goals:
            # Calculate the Manhattan distance between the current crate and goal
            distance = manhattan_distance(goal, crate)
            # Updates the minimum distance if the current distance is smaller.
            min_distance = min(min_distance, distance)
        # Adds the minimum distance for the current crate to the total heuristic value.
        heuristic_value += min_distance

    #  Stores the calculated heuristic value for the current state in the cache.
    cache[state] = heuristic_value

    # Return the calculated heuristic value
    return heuristic_value

def is_deadlock(problem: SokobanProblem, state: SokobanState, crate: Point) -> float:
    """
    Checks if the given crate position leads to a deadlock in the Sokoban game.

    Parameters:
    - problem (SokobanProblem): The Sokoban problem instance.
    - state (SokobanState): The current state of the Sokoban game.
    - crate (Point): The position of the crate to be checked for deadlock.

    Returns:
    - bool: True if the crate position leads to a deadlock, False otherwise.
    """
    
    # Check corner condition
    def is_corner():
        """
        Checks if the crate is in a corner, where it has no available moves.

        Returns:
        - bool: True if the crate is in a corner, False otherwise.
        """
        
        if (
            (Point(crate.x - 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y - 1) not in state.layout.walkable) or 
            (Point(crate.x - 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y + 1) not in state.layout.walkable) or
            (Point(crate.x + 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y - 1) not in state.layout.walkable) or
            (Point(crate.x + 1, crate.y) not in state.layout.walkable and Point(crate.x, crate.y + 1) not in state.layout.walkable)
            ):
            return True
        
    # Check conditions for unsolvable positions
    def is_unsolvable_position():
        """
        Checks if the crate is in an unsolvable position, based on specific conditions.

        Returns:
        - bool: True if the crate is in an unsolvable position, False otherwise.
        """
        
        condition1 = (
            (crate.x == problem.layout.width - 2 and len([goal for goal in problem.layout.goals if goal.x == problem.layout.width - 2]) == 0)
            or (crate.x == 1 and len([goal for goal in problem.layout.goals if goal.x == 1]) == 0)
            or (crate.y == problem.layout.height - 2 and len([goal for goal in problem.layout.goals if goal.y == problem.layout.height - 2]) == 0)
            or (crate.y == 1 and len([goal for goal in problem.layout.goals if goal.y == 1]) == 0)
        )
        
        condition2 = (
            (Point(crate.x - 1, crate.y) in state.crates and (crate.x - 2 == 0 or crate.x + 2 == state.layout.width))
            or (Point(crate.x + 1, crate.y) in state.crates and (crate.x - 1 == 0 or crate.x + 3 == state.layout.width))
            or (Point(crate.x, crate.y - 1) in state.crates and (crate.y - 2 == 0 or crate.y + 2 == state.layout.height))
            or (Point(crate.x, crate.y + 1) in state.crates and (crate.y - 1 == 0 or crate.y + 3 == state.layout.height) or ())
        )

        return condition1 or condition2    
       
    # Checks if the first wall (to the left) is blocking the crate.
    def check_left_wall() -> int:
        """
        Checks if the first wall (to the left) is blocking the crate.

        Returns:
        - int: 1 if the wall blocks the crate, 0 otherwise.
        """
        if (Point(crate.x - 1, crate.y) not in state.layout.walkable or 
            Point(crate.x - 1, crate.y) in state.crates or 
            crate.x - 1 == 0):
            return 1
        return 0

    # Checks if the second wall (to the right) is blocking the crate.
    def check_right_wall() -> int:
        """
        Checks if the second wall (to the right) is blocking the crate.

        Returns:
        - int: 1 if the wall blocks the crate, 0 otherwise.
        """
        if (Point(crate.x + 1, crate.y) not in state.layout.walkable or 
            Point(crate.x + 1, crate.y) in state.crates or 
            crate.x + 1 == state.layout.width - 1):
            return 1
        return 0

    # Checks if the third wall (above) is blocking the crate.
    def check_above_wall() -> int:
        """
        Checks if the third wall (above) is blocking the crate.

        Returns:
        - int: 1 if the wall blocks the crate, 0 otherwise.
        """
        if (Point(crate.x, crate.y + 1) not in state.layout.walkable or 
            Point(crate.x, crate.y + 1) in state.crates or 
            crate.y - 1 == 0):
            return 1
        return 0

    # Checks if the fourth wall (below) is blocking the crate.
    def check_below_walls() -> int:
        """
        Checks if the fourth wall (below) is blocking the crate.

        Returns:
        - int: 1 if the wall blocks the crate, 0 otherwise.
        """
        if (Point(crate.x, crate.y - 1) not in state.layout.walkable or 
            Point(crate.x, crate.y - 1) in state.crates or 
            crate.y + 1 == state.layout.height - 1):
            return 1
        return 0

    # Checks if the crate is blocked by three or more walls in any direction.
    def check_all_walls() -> bool:
        """
        Checks if the crate is blocked by three or more walls in any direction.

        Returns:
        - bool: True if the crate is blocked by three or more walls, False otherwise.
        """
        return (check_left_wall() + check_right_wall() + check_above_wall() + check_below_walls()) >= 3

    if is_corner() or is_unsolvable_position() or check_all_walls():
        return True # The crate position leads to a deadlock
    return False
