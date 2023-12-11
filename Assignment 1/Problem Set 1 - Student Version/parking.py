from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers.utils import NotImplemented

#TODO: (Optional) Instead of Any, you can define a type for the parking state
ParkingState = Any

# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]

# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[Point]    # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]      # A tuple of points where state[i] is the position of car 'i'. 
    slots: Dict[Point, int] # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the lot of car 'i') for every position.
                            # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int              # The width of the parking lot.
    height: int             # The height of the parking lot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        #TODO: ADD YOUR CODE HERE
        """
        Get the initial state of the parking problem.

        Returns:
            ParkingState: The initial state where each car is in its initial position.
        """        
        return self.cars # the initial state of the parking problem
    
    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        #TODO: ADD YOUR CODE HERE
        """
        Check if the given state is a goal state.

        Args:
            state (ParkingState): The state to check.

        Returns:
            bool: True if the state is a goal, False otherwise.
        """
        # Loop for car's position in the given state.
        for car_index, car_position in enumerate(state):
            # get the parking slot indicated in the slots dictionary.
            parking_slot = self.slots.get(car_position)
            # checks if the position of the car in the state matches the parking slot
            if parking_slot != car_index:
                return False # return false if it's not the goal
        return True # return true if it's the goal
    
    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        #TODO: ADD YOUR CODE HERE
        """
        Get a list of all possible actions that can be applied to the given state.

        Args:
            state (ParkingState): The current state.

        Returns:
            List[ParkingAction]: A list of valid parking actions.
        """
        actions = []
        # Loop for car's position in the given state.
        for car_index, car_position in enumerate(state):
            # Loop for each direction
            for direction in Direction:
                # Calculate the new position with the direction
                new_position = car_position + Direction._Vectors[direction]

                # Check if new position is a place that car can be, and new_position != state[car_index], and new_position not in state
                if new_position in self.passages and new_position != state[car_index] and new_position not in state:
                    actions.append((car_index, direction)) # Add action to the actions
        return actions # Return all actions
    
    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        #TODO: ADD YOUR CODE HERE
        """
        Get the new state resulting from applying the given action to the current state.

        Args:
            state (ParkingState): The current state.
            action (ParkingAction): The action to apply.

        Returns:
            ParkingState: The new state after applying the action.
        """

        # Get car index and direction from the action
        car_index, direction = action
        # Get car position from the state
        car_position = state[car_index]

        # Calcuate the new state after the moving
        new_position = car_position + Direction._Vectors[direction]

        # Create a copy of the current state
        new_state = list(state)
        # update the new state's position for the car with the new_position.
        new_state[car_index] = new_position
        # The reason for converting it to a tuple is to maintain immutability, 
        # which is important for ensuring that states are not accidentally modified after creation.
        return tuple(new_state)
    
    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        #TODO: ADD YOUR CODE HERE
        """
        Get the cost of applying the given action to the current state.

        Args:
            state (ParkingState): The current state.
            action (ParkingAction): The action to apply.

        Returns:
            float: The cost of the action.
        """

        # Get car index and direction from the action
        car_index, direction = action
        car_rank = 26 - car_index # Calculate the rank based on the car's index (adding 1 to handle 1-based indexing)
        
        # Get car position from the state
        car_position = state[car_index]
        
        # Check if car is moving into its own slot
        if car_position in self.slots:
            return car_rank # Return the car rank.
        
        # Check if the action moves the car into another employee's parking slot
        else:
            # Lopp for all slots for another employee's parking slot
            for slot, owner_index in self.slots.items():
                # Check if owner of the slot not the car owner, car position after direction equal to the slot
                if owner_index != car_index and car_position  + Direction._Vectors[direction] == slot:
                    return car_rank + 100 # Return the car rank with penalty 100.

        return car_rank # Car is moving to an empty space
    
     # Read a parking problem from text containing a grid of tiles
    
    @staticmethod
    def from_text(text: str) -> 'ParkingProblem':
        passages =  set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == '.':
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord('A')] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position:index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'ParkingProblem':
        with open(path, 'r') as f:
            return ParkingProblem.from_text(f.read())
    
