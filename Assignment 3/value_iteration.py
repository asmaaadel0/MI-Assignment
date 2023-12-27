from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
from helpers.utils import NotImplemented

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        #TODO: Complete this function
        # NotImplemented()
        if self.mdp.is_terminal(state):
            return 0
        utility = max(sum( self.mdp.get_successor(state, action)[next_state] * (self.mdp.get_reward(state, action, next_state) + self.discount_factor * self.utilities[next_state]) for next_state in self.mdp.get_successor(state, action) ) for action in self.mdp.get_actions(state) )
        return utility
    
    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        #TODO: Complete this function
        # NotImplemented()
        """
        Updates the utilities of all states in the Markov Decision Process (MDP) based on the Bellman equation.

        Args:
            tolerance (float): A threshold for the maximum allowable change in utility values during an update. 
                            If the change is below this threshold, the function will indicate convergence.

        Returns:
            bool: Returns True if the maximum change in utility values is less than or equal to the specified tolerance,
                indicating potential convergence. Returns False otherwise.

        This function iterates over all states in the MDP, computing updated utilities based on the Bellman equation. 
        It then checks if the largest change in utility is within the specified tolerance, signaling convergence.
        """
        # Initialize an empty dictionary to store utility updates for each state
        utility_updates = {}

        # Iterate through all states in the Markov Decision Process (MDP)
        for state in self.mdp.get_states():
            # Compute the updated utility for each state using the Bellman equation and store it
            utility_updates[state] = self.compute_bellman(state)

        # Calculate the maximum change in utility across all states
        max_change = max(abs(utility_updates[state] - self.utilities[state]) for state in self.mdp.get_states())

        # Update the utilities of the agent with the newly computed utilities
        for state in self.mdp.get_states():
            self.utilities[state] = utility_updates[state]

        # Return True if the maximum change in utility is less than or equal to the tolerance; False otherwise
        return max_change <= tolerance

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        #TODO: Complete this function to apply value iteration for the given number of iterations
        # NotImplemented()
        """
        Applies value iteration to update the agent's utilities for a specified number of iterations or until convergence.

        Args:
            iterations (Optional[int]): The number of iterations to run value iteration. If None, the function runs indefinitely 
                                        until convergence is detected.
            tolerance (float): A threshold for determining convergence during utility updates. If the maximum change in utilities 
                            is below this threshold, the function considers the process as converged.

        Returns:
            int: The number of iterations completed before stopping. This could be due to reaching the maximum number of iterations 
                or achieving convergence.

        The function continuously updates utilities using the `update` method. It stops either after a specified number of iterations 
        or when the utilities converge within the given tolerance.
        """
        # Initialize the iteration counter
        iteration = 0

        # Continuously update utilities until the specified number of iterations is reached or early stopping condition is met
        while iterations is None or iteration < iterations:
            # Increment the iteration counter
            iteration += 1

            # Update utilities and check for convergence; break if converged
            if self.update(tolerance):
                break

        # Return the number of iterations completed
        return iteration
    
    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        #TODO: Complete this function
        # NotImplemented()
        """
            Determines the best action to take in a given state based on the current utilities and the Markov Decision Process (MDP).

            Args:
                env (Environment[S, A]): The environment in which the agent operates, defined by states S and actions A.
                state (S): The current state for which the best action is to be determined.

            Returns:
                A: The optimal action for the given state as per the learned utilities. If the state is terminal, returns None.

            The function calculates the expected utility of each possible action from the current state and selects the action 
            with the highest expected utility. If the state is terminal, it returns None, indicating no further action is required.
            """
        # Check if the current state is terminal; return None if it is
        if self.mdp.is_terminal(state):
            return None   

        # Determine the best action based on the learned utilities and the MDP
        action = max(
            self.mdp.get_actions(state),
            key=lambda action: sum(
                self.mdp.get_successor(state, action)[next_state] * 
                (self.mdp.get_reward(state, action, next_state) + 
                self.discount_factor * self.utilities[next_state])
                for next_state in self.mdp.get_successor(state, action)
            )
        )

        # Return the action that maximizes the expected utility
        return action
    
    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
